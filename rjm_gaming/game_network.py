# -*- coding: utf-8 -*-
"""
Created on Tue May  3 10:08:07 2022

@author: Robert J McGinness
"""

import socket
from typing import Any
from enum import Enum

from game_utilities import CommsModule
from game_utilities import GameCommsError
from game_utilities import FileDataAccess

class HTTPStatusCode(Enum):
    ######should complete this with all of them
    VERSION = 'HTTP/1.1'
    OK = VERSION + ' 200 OK\n'
    NOT_FOUND = VERSION + ' 404 Not Found\n'
    INTERNAL_ERROR = VERSION + ' 500 Internal Server Error\n'

status_codes = {200: HTTPStatusCode.OK.value,
                404: HTTPStatusCode.NOT_FOUND.value,
                500: HTTPStatusCode.INTERNAL_ERROR.value}


class HTTPCommsModule(CommsModule):
    def __init__(self, connection: socket.socket, max_clients: int = 1) -> None:
        super().__init__(connection, connection)
        self.__connection = connection
        self.__max_connections = max_clients
    
    def write(self, data: Any) -> Any:
        try:
            self.__connection.sendall(bytes(data.encode('utf-8')))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            raise GameCommsError from e
    
    def read(self) -> Any:
        try:
            return self.__connection.recv(2048).decode()###### may want to parse Content-Type to decide how to decode (ex. json)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            raise GameCommsError from e
    
    def render(self, data: Any, status_code: int = 200) -> None:
        response = ''
        try:
            response += status_codes[status_code]
        except KeyError:
            response += status_codes[500]
        
        response += '\r\n' + str(data)#####will this cause an error, if bytes (check for b' in output)
        
        self.write(response)
    
    def render_file(self, file_name: str, status_code: int = 200) -> None:
        file_access = FileDataAccess(file_name)#read file as binary
        
        ######what about Content-Type
        
        self.render(file_access.data, status_code)
    
    def close(self) -> None:
        try:
            self.__connection.close()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            raise GameCommsError from e

class ServerClient:
    def __init__(self, name: str, client_id: str, authenticated: bool = False) -> None:
        self.__name = name
        self.__id = client_id
        self.__authenticated = authenticated
        
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def client_id(self) -> str:
        return self.__id
    
    @property
    def isauthenticated(self) -> bool:
        return self.__authenticated

if __name__ == '__main__':
    print(HTTPStatusCode.OK.value)
    
    import sys
    sys.exit()
    