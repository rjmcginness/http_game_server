# -*- coding: utf-8 -*-
"""
Created on Thu May  5 21:50:29 2022

@author: Robert J McGinness
"""

import time

from game_network import HTTPCommsModule
from game_network import HTTPHeader
from game_network import HTTPRequest
from game_network import HTTPSession
from game_utilities import FileDataAccess
from config import Config



class ServerClient:
    def __init__(self, name: str, session: HTTPSession, authenticated: bool = False) -> None:
        self.__name = name
        self.__session = session
        self.__authenticated = authenticated
        
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def client_id(self) -> str:
        return self.__session.client_id
    
    @property
    def isauthenticated(self) -> bool:
        return self.__authenticated
    
    def __repr__(self) -> str:
        return f'name={self.__name} id={self.__id} authenticated={self.__authenticated}'

class Authenticator:
    def __init__(self, config: Config, **kwargs) -> None:
        super().__init__()
        self.__request = kwargs['request']
        self.__config: Config = config
        self.__client: ServerClient = None
        self.__authenticate(**kwargs)
    
    # def __send_login_form(self) -> None:
    #     header = HTTPHeader()
    #     header.content_type = 'text/html; charset=utf-8'
    #     client_id = self.__request.name + str(time.time())
    #     session = HTTPSession(client_id)
    #     self.__comms.render(session.form_file_insert(self.__config.LOGIN_FORM))
        
    #     self.__client = ServerClient('Robert', session, authenticated=True)
    
    def __authenticate(self, **kwargs) -> None:
     
        print('AUTHENTICATE KWARGS:', kwargs)
        print('KWARGS SESSION', kwargs['request'].session)
        #################################################################
        ######FAKED FOR NOW
        ######HIT DB INSTEAD
        #################################################################
        try:
            header = kwargs['header']
            query_idx = header.index('?') + 1 # starts one beyond ?
            username, password = tuple(header[query_idx:].split('&'))
            username = username.split('=')[1]
            password = password.split('=')[1]
            
            ##############################################
            ######Authenicate username and password in DB
            
            self.__client = ServerClient(username,
                                         kwargs['request'].session,
                                         authenticated=True)
        except ValueError:
            self.__client = None
    
    @property
    def client(self) -> ServerClient:
        return self.__client
    
    @property
    def success(self) -> bool:
        if self.__client is None:
            return False
        
        return self.__client.isauthenticated
    
if __name__ == '__main__':
    from sys import exit
    exit()
    # from game_network import HTTPCommsModule
    # import socket
    
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    #     server.bind(('localhost', 6500))
    #     server.listen(1)
    #     connection, address = server.accept()
        
    #     comms = HTTPCommsModule(connection, time_out=None)
    #     auth = Authenticator(comms, Config())
    #     if auth.success:
    #         print(auth.client)
        
    #     comms.close()