# -*- coding: utf-8 -*-
"""
Created on Thu May  5 21:50:29 2022

@author: Robert J McGinness
"""

import time

from game_network import HTTPCommsModule
from game_network import HTTPHeader
from game_utilities import FileDataAccess
from config import Config



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
    
    def __repr__(self) -> str:
        return f'name={self.__name} id={self.__id} authenticated={self.__authenticated}'

class Authenticator():
    def __init__(self, comms: HTTPCommsModule, config: Config) -> None:
        super().__init__()
        self.__comms: HTTPCommsModule = comms
        self.__config: Config = config
        self.__client: ServerClient = None
        self.__authenticate()
    
    def __authenticate(self) -> None:
        #print(self.__comms.read())#get initital GET for page MAYBE THIS SHOULD NOT BE HERE
        header = HTTPHeader()
        header.content_type = 'text/html; charset=utf-8'
        self.__comms.render_file(self.__config.LOGIN_FORM, header)
        print("RENDERED")
        
        request = ''
        while '/auth?' not in request:
            #time.sleep(1)
            print(request.split('\n'))
            request = self.__comms.read()
        print(request)
            # print(connection.recv(1024))
            # print(auth_html())
            # connection.sendall(auth_html())
            # print(connection.recv(1024))
        
        #####HIT DB FOR AUTHENTICATION
        ######FAKED FOR NOW
        self.__client = ServerClient('Robert', str(time.time()), authenticated=True)
    
    @property
    def client(self) -> ServerClient:
        return self.__client
    
    @property
    def success(self) -> bool:
        return self.__client.isauthenticated
    
if __name__ == '__main__':
    from game_network import HTTPCommsModule
    import socket
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('localhost', 6500))
        server.listen(1)
        connection, address = server.accept()
        
        comms = HTTPCommsModule(connection, time_out=None)
        auth = Authenticator(comms, Config())
        if auth.success:
            print(auth.client)
        
        comms.close()