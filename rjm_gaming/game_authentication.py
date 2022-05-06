# -*- coding: utf-8 -*-
"""
Created on Thu May  5 21:50:29 2022

@author: Robert J McGinness
"""

import time

from game_utilities import CommsModule
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

class Authenticator():
    def __init__(self, comms: CommsModule, config: Config) -> None:
        super().__init__()
        self.__comms: CommsModule = comms
        self.__config: Config = config
        self.__client: ServerClient = None
        self.__authenticate()
    
    def __authenticate(self) -> None:
        
        file_access = FileDataAccess(self.__config.LOGIN_FORM)
        print(file_access.data)
        self.__comms.write(file_access.data)
        request = self.__comms.read_input()
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