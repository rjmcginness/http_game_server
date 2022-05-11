# -*- coding: utf-8 -*-
"""
Created on Thu May  5 21:50:29 2022

@author: Robert J McGinness
"""

from game_network import HTTPSession
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
    
    def __eq__(self, client2) -> bool:
        return (self.__name == client2.name and 
                self.client_id == client2.client_id)

class Authenticator:
    def __init__(self, config: Config, **kwargs) -> None:
        super().__init__()
        self.__request = kwargs['request']
        self.__config: Config = config
        self.__client: ServerClient = None
        self.__authenticate(**kwargs)
    
    def __authenticate(self, **kwargs) -> None:
    
        #################################################################
        ######FAKED FOR NOW
        ######HIT DB INSTEAD
        #################################################################
        try:
            header = kwargs['request_type'].split(' ')
            query_pairs = header[1].split('&')
            username = ''
            password = ''
            for query_pair in query_pairs:
                if 'username=' in query_pair:
                    username = query_pair.split('username=')[1]
                if 'password=' in query_pair:
                    password = query_pair.split('password=')[1]
            
            
            ##############################################
            ######Authenicate username and password in DB
            
            self.__client = ServerClient(username,
                                         self.__request.session,
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