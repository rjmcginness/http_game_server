# -*- coding: utf-8 -*-
"""
Created on Tue May  3 10:08:07 2022

@author: Robert J McGinness
"""

import socket
from typing import Any
from typing import Optional
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

class HTTPHeader:
    def __init__(self) -> None:
        self.__accept: str = ''
        self.__accept_char: str = ''
        self.__accept_enc: str = ''
        self.__accept_lang: str = ''
        self.__connection: str = ''
        self.__content_len: str = ''
        self.__content_type: str = ''
    
    @property
    def accept(self) -> str:
        return self.__accept
    
    @accept.setter
    def accept(self, data: str) -> None:
        self.__accept = f'Accept: {data}\n'
    
    @property
    def accept_charset(self) -> str:
        return self.__accept_char
    
    @accept_charset.setter
    def accept_charset(self, data: str) -> None:
        self.__accept_char = f'Accept-Charset: {data}\n'
    
    @property
    def accept_encoding(self) -> str:
        return self.__accept_enc
    
    @accept_encoding.setter
    def accept_encoding(self, data: str) -> None:
        self.__accept_enc = f'Accept-Encoding: {data}\n'
    
    @property
    def accept_language(self) -> str:
        return self.__accept_lang
    
    @accept_language.setter
    def accept_language(self, data: str) -> None:
        self.__accept_lang = f'Accept-Language: {data}\n'
    
    @property
    def connection(self) -> str:
        return self.__connection
    
    @connection.setter
    def connection(self, data: str) -> None:
        self.__connection = f'Connection: {data}\n'
    
    @property
    def content_length(self) -> str:
        return self.__content_len
    
    @content_length.setter
    def content_length(self, data: str) -> None:
        self.__content_len = f'Content-Length: {data}\n'
    
    @property
    def content_type(self) -> str:
        return self.__content_type
    
    @content_type.setter
    def content_type(self, data: str) -> None:
        self.__content_type = f'Content-Type: {data}\n'
    
    def __repr__(self) -> str:
        return (self.accept + self.accept_charset + self.accept_encoding +\
                self.accept_language + self.connection + self.content_length +\
                self.content_type + '\r\n')

class HTTPCommsModule(CommsModule):
    def __init__(self, connection: socket.socket,
                 time_out:int = None,
                 max_clients: int = 1) -> None:
        super().__init__(connection, connection)
        self.__connection = connection
        self.__connection.settimeout(time_out)
        self.__max_connections = max_clients
    
    def write(self, data: Any) -> Any:
        try:
            if not isinstance(data, bytes):
                data = bytes(data.encode('utf-8'))
            
            # self.__connection.sendall(data)
            data_sent = 0
            while data_sent < len(data):
                data_sent += self.__connection.send(data)
                
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            raise GameCommsError(e) from e
    
    def read(self) -> Any:
        try:
            return self.__connection.recv(1024).decode()###### may want to parse Content-Type to decide how to decode (ex. json)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            raise GameCommsError(e) from e
    
    def render(self, data: Any, header: Optional[HTTPHeader] = None,
                                               status_code: int = 200) -> None:
                       
        response = ''
        try:
            response += status_codes[status_code]
        except KeyError:
            response += status_codes[500]
        
        response += str(header) + str(data) + '\n'#####will this cause an error, if bytes (check for b' in output)
          
        self.write(response)
    
    def render_file(self, file_name: str,
                    header: Optional[HTTPHeader] = None,
                    status_code: int = 200) -> None:
                    
        
        file_access = FileDataAccess(file_name, raw=False)#read file as text
        
        self.render(file_access.data, header, status_code)
    
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
    
    from config import Config
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('localhost', 7700))
        server.listen(1)
        connection, address = server.accept()
        with connection:
            comms = HTTPCommsModule(connection)
            
            print('BEFORE RENDER')
            print(comms.read())
            
            header = HTTPHeader()
            header.content_type = 'text/html; charset=utf-8'
            comms.render_file(Config().LOGIN_FORM, header)
            
            
            print("GET")
            print(comms.read())
            print(comms.read())
            
            # result = ''
            # while not result:
            #     result = comms.read()
            
            # print(result)
    
    import sys
    sys.exit()
    