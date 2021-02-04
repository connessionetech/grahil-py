'''
This file is part of `Grahil` 
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

from oneadmin.handlers import base
from tornado.web import url


def get_url_patterns(rest:bool, ws:bool):
    
    if rest and not ws:
        return [
            url(r"/", base.MainHandler),
            url(r"/file/read", base.FileReadHandler),
            url(r"/file/write", base.FileWriteHandler),
            url(r"/file/download", base.FileDownloadHandler),
            url(r"/file/delete", base.FileDeleteeHandler)
            ]
    elif ws and not rest:
        return [
            url(r"/ws", base.WebSocketHandler),
            ]
    elif ws and rest:
        return [
            url(r"/", base.MainHandler),
            url(r"/file/read", base.FileReadHandler),
            url(r"/file/write", base.FileWriteHandler),
            url(r"/file/download", base.FileDownloadHandler),
            url(r"/file/delete", base.FileDeleteeHandler),
            url(r"/ws", base.WebSocketHandler),
            ]