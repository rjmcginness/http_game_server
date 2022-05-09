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
        self.__host: str = ''
    
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
    
    @property
    def host(self) -> str:
        return self.__host
    
    @host.setter
    def host(self, data: str) -> None:
        self.__host = f'Host: {data}\n'
    
    def __repr__(self) -> str:
        return (self.host + self.accept + self.accept_charset  +\
                self.accept_encoding + self.accept_language +\
                self.connection + self.content_length + self.content_type + '\r\n')



class HTTPCommsModule:
    def __init__(self, connection: socket.socket,
                 time_out:int = None,
                 max_clients: int = 1) -> None:
        # super().__init__(connection, connection)
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
            print(self.__connection)
            return self.__connection.recv(2048).decode() # DOES SIZE MATTER???
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
        
        response += str(header) + str(data)#####will this cause an error, if bytes (check for b' in output)
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

class HTTPSession:
    def __init__(self, client_id: str) -> None:
        self.__client_id = client_id
    
    def form_insert(self, form: str) -> str:
        id_tag = '<input hidden type="hidden" name="identifier" '
        id_tag += f'value="{self.__client_id}"/>\n'
        
        return form.replace('</form>', id_tag + '</form>')
    
    def form_file_insert(self, file_name: str) -> str:
        form = ''
        with open(file_name, 'rt') as form_file:
            form = form_file.read()
        
        form.strip()
        form += '\r\n'
        
        return self.form_insert(form)
    
    @property
    def client_id(self) -> str:
        return self.__client_id
    
    def __repr__(self) -> str:
        return self.__client_id

class HTTPRequest:
    def __init__(self, connection: socket.socket) -> None:
        self.__name = connection.getpeername()[1] # client port number
        self.__connection = HTTPCommsModule(connection)
        self.__request = self.__connection.read()
        self.__parse_session()
    
    def __parse_session(self) -> None:
        ''' Parses the session identifier in the request.
            Parses for the query identifier=IDENTIFIER~
            from form tag <input hidden type="hidden"
            name="identifier" value="IDENTIFIER"/>, where 
            IDENTIFIER is the session ID
            
            Stored a new HTTPSession object with client identifier,
            if found, or None.
        '''
        print(f"REQUEST:\n{self.__request}")
        try:
            found_at_idx = self.__request.index('identifier=')
            start_idx = found_at_idx+len('identifier=')
            end_idx = self.__request[start_idx:].index(' ')
            identifier = self.__request[start_idx:start_idx + end_idx]
            print(f'IDENTIFIER-----: {identifier}')
            self.__session = HTTPSession(identifier)
        except (ValueError, IndexError):
            self.__session = None
    
    @property
    def name(self) -> str:
        return str(self.__name)
    
    @property
    def connection(self) -> HTTPCommsModule:
        return self.__connection
    
    @property
    def session(self) -> Optional[HTTPSession]:
        
        return self.__session
    
    @session.setter
    def session(self, http_session: HTTPSession) -> None:
        self.__session = http_session
    
    @property
    def request(self) -> str:
        return self.__request
    
    def __repr__(self) -> str:
        return self.__request
    



if __name__ == '__main__':
    from sys import exit
    exit()
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

'''
GET /auth?username=Robert&password=pass&identifier=645731652113574.3543987 HTTP/1.1
Host: localhost:6500
User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Connection: keep-alive
Referer: http://localhost:6500/
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Accept-Encoding: gzip, deflate
'''