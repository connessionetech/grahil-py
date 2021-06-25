import requests
import tempfile
import os
import zipfile
import pathlib
import shutil
import imp
from jsonmerge import merge
from jsonschema import validate
import json


''' Check if file is downloadable '''
def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True

# Check manifest to determien what is the latest version available

# Download file
url = 'https://grahil.s3.amazonaws.com/grahil-py.zip'
current_program_path = "/home/rajdeeprath/github/grahil-py/"
versions_module_name = "version.py"

def_conf_schema = {
            "properties" : {
                "enabled": {
                    "type": "boolean",
                    "mergeStrategy": "overwrite"
                },
                "klass": {
                    "type": "string",
                    "mergeStrategy": "overwrite"
                },
                "conf": {
                    "type": "object",
                    "mergeStrategy": "objectMerge"
                }
            },
            "required": ["enabled", "klass", "conf"]
        }



def_rules_schema = {
            "properties" : {
                "id": {
                    "type": "boolean",
                    "mergeStrategy": "overwrite"
                },
                "enabled": {
                    "type": "boolean",
                    "mergeStrategy": "overwrite"
                },
                "listen-to": {
                    "type": "string",
                    "mergeStrategy": "overwrite"
                },
                "trigger": {
                    "type": "object",
                    "mergeStrategy": "objectMerge"
                },
                "response": {
                    "type": "object",
                    "mergeStrategy": "objectMerge"
                }
            },
            "required": ["id", "description", "listen-to", "enabled", "trigger", "response"]
        }

def_master_configuration_schema = {
            "properties" : {
                "configuration": {
                    "properties" : {
                        "base_package": {
                            "type": "string",
                            "mergeStrategy": "overwrite"
                        },
                        "server": {
                            "type": "object",
                            "mergeStrategy": "objectMerge"
                        },
                        "ssl": {
                            "type": "object",
                            "mergeStrategy": "objectMerge"
                        },
                        "security": {
                            "type": "object",
                            "mergeStrategy": "objectMerge"
                        },
                        "modules": {
                            "type": "object",
                            "mergeStrategy": "objectMerge"
                        }                    
                    },
                     "required": ["base_package", "server", "ssl", "security", "modules"]
                }                
            },
            "required": ["configuration"]
        }

temp_dir_for_latest = tempfile.TemporaryDirectory() # Where to extract and hold the latest files
temp_dir_for_existing = tempfile.TemporaryDirectory() # Where to copy and work with the existing files
temp_dir_for_download = tempfile.TemporaryDirectory() # Where to download latest build
temp_dir_for_updated = tempfile.TemporaryDirectory() # Where to build & test the update before installation

if is_downloadable(url):
    # download file
    path_to_zip_file = os.path.join(temp_dir_for_download.name, "grahil-latest.zip")
    r = requests.get(url, allow_redirects=True)
    open(path_to_zip_file, 'wb').write(r.content)
    
    # extract file to a tmp location
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir_for_latest.name)
    path = os.path.join(temp_dir_for_latest.name, "run.py")
    if pathlib.Path(str(path)).exists():
        print ("latest extraction success")
        pass
    
    # copy existing program installation to a tmp location
    if os.path.exists(temp_dir_for_existing.name):
        shutil.rmtree(temp_dir_for_existing.name)
        
    shutil.copytree(current_program_path, temp_dir_for_existing.name)
    path2 = os.path.join(temp_dir_for_existing.name, "run.py")
    if pathlib.Path(str(path2)).exists():
        print ("existing installation copy success")
        pass

    ## compare versions
    old_version_module_path = os.path.join(temp_dir_for_existing.name, "oneadmin", "version.py")
    old_version_module = imp.load_source(versions_module_name, old_version_module_path)
    old_version = old_version_module.__version__.split(".")

    new_version_module_path = os.path.join(temp_dir_for_latest.name, "oneadmin", "version.py")
    new_version_module = imp.load_source(temp_dir_for_latest.name, new_version_module_path)
    new_version = new_version_module.__version__.split(".")

    upgrade=False    
    if new_version[0] > old_version[0]:
        upgrade=True
    elif (new_version[0] == old_version[0]) and  (new_version[1] > old_version[1]):
        upgrade=True
    elif (new_version[0] == old_version[0]) and  (new_version[1] == old_version[1]) and (new_version[2] > old_version[2]):
        upgrade=True

    print("upgrade = "+str(upgrade))
    upgrade = True


    if upgrade:
        print("ready to upgrade")




        ## Merge configuration json files
        #exisitng_configs_location=os.path.join(temp_dir_for_existing.name, "oneadmin", "modules", "config")
        #new_configs_location=os.path.join(temp_dir_for_latest.name, "oneadmin", "modules", "config")

        ## Merge reaction engine rules json files
        #exisitng_rules_location=os.path.join(temp_dir_for_existing.name, "oneadmin", "modules", "config")
        #new_rules_location=os.path.join(temp_dir_for_latest.name, "oneadmin", "modules", "config")




        ## First we copy all old files into update workspace
        if os.path.exists(temp_dir_for_updated.name):
            shutil.rmtree(temp_dir_for_updated.name)

        shutil.copytree(temp_dir_for_existing.name, temp_dir_for_updated.name)
        path2 = os.path.join(temp_dir_for_updated.name, "run.py")
        if pathlib.Path(str(path2)).exists():
            print ("existing installation copy to update workspace success")


        # Collect list of all new files (json and otherwise)
        latest_files = []
        latest_json_files = []
        for subdir, dirs, files in os.walk(temp_dir_for_latest.name):
            for file in files:
                if not file.endswith(".json"):
                    program_file = os.path.join(subdir, str(file))
                    latest_files.append(program_file)
                else:
                    json_file = os.path.join(subdir, str(file))
                    latest_json_files.append(json_file)
                
        
        # then we overwrite new files on old files in updated workspace (minus json files)
        for file in latest_files:
            old_file_in_update_workspace = str(file).replace(temp_dir_for_latest.name, temp_dir_for_updated.name)
            dest = shutil.copy2(old_file_in_update_workspace, file)


        ## check, validate and merge json configuration files        
        for file in latest_json_files:
            old_file_in_update_workspace = str(file).replace(temp_dir_for_latest.name, temp_dir_for_updated.name)

            with open(old_file_in_update_workspace, 'r') as old_json_file:
                base_data = old_json_file.read()
                base_obj = json.loads(base_data)
            
                with open(file, 'r') as latest_json_file:
                    latest_data = latest_json_file.read()
                    latest_obj = json.loads(latest_data)

                if "conf/" in old_file_in_update_workspace:
                    validate(base_obj, def_conf_schema)
                    validate(latest_obj, def_conf_schema)
                    updated_data = merge(base_obj, latest_obj)
                elif "rules/" in old_file_in_update_workspace:
                    validate(base_obj, def_rules_schema)
                    validate(latest_obj, def_rules_schema)
                    updated_data = merge(base_obj, latest_obj)
                elif "configuration.json" in old_file_in_update_workspace:
                    validate(base_obj, def_master_configuration_schema)
                    validate(latest_obj, def_master_configuration_schema)
                    updated_data = merge(base_obj, latest_obj)                    
                else:
                    print("Unsure of how to merge thasi file... skipping")
                    continue


                with open(old_file_in_update_workspace, "w") as outfile:
                        outfile.write(json.dumps(updated_data))
                    
                    




        ## verify everything

        ## stop running program service

        ## backup everything to a safe location

        ## overwrite everything from prepared package to program location

        ## start program

        ## verify thisng are running ok and there are no errors

        ## if anything is not working as expected cancel upgrade and restore backup

        ## start program

    else:
        print("cannot upgrade")

else:
    print ("File is not downloadable")
