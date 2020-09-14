'''
This file is part of `Reactivity` 
Copyright 2018 Connessione Technologies

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import json
import logging
import os
from oneadmin.exceptions import ConfigurationLoadError



class Configuration(object):
    '''
    classdocs
    '''

    def __init__(self, conf_file):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.__conf_file = conf_file
        self.config = None
        
        
    def load(self):
        
        self.logger.info("Loading configuration data")
        
        try:
            self.logger.info("Loading %s", self.__conf_file)
            if os.path.exists(self.__conf_file):
                with open(self.__conf_file, 'r+') as json_data_file:
                    self.config = json.load(json_data_file)["configuration"]
            else:
                raise FileNotFoundError("File : " + self.__conf_file + " does not exist.")
        
        except Exception as e:
            err = "Unable to load primary configuration " + str(e)
            self.logger.error(err)
            raise ConfigurationLoadError(err)
        
        
    @property
    def data(self):
        return self.config

