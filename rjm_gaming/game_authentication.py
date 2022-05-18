# -*- coding: utf-8 -*-
"""
Created on Thu May  5 21:50:29 2022

@author: Robert J McGinness
"""

from typing import Dict

from config import Config
from game_network import remove_http_pluses


class ServerClient:
    def __init__(self, name: str, session: str, authenticated: bool = False) -> None:
        self.__name = name
        self.__session = session
        self.__authenticated = authenticated
        
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def client_id(self) -> str:
        return self.__session
    
    @property
    def isauthenticated(self) -> bool:
        return self.__authenticated
    
    def __repr__(self) -> str:
        return f'name={self.__name} id={self.__session} authenticated={self.__authenticated}'
    
    def __eq__(self, client2) -> bool:
        return (self.__name == client2.name and 
                self.client_id == client2.client_id)
    
    # @property
    # def encoding(self) -> Dict:
    #     return {'_meta':{'module':self.__module__,
    #                      'cls':self.__class__.__name__},
    #             'name':self.__name,
    #             'id':self.__id,
    #             'experience':self.__experience}
    
    # @classmethod
    # def decode(cls: Type, obj: object):
    #     try:
    #         if obj['_meta']['cls'] == cls.__name__:
    #             return cls(obj['id'], obj['name'], experience=obj['experience'])
    #     except KeyError:
    #         return obj

class Authenticator:
    def __init__(self, config: Config, **kwargs) -> None:
        # super().__init__()
        self.__request = kwargs['request']
        self.__config: Config = config
        self.__client: ServerClient = None
        self.__authenticate(**kwargs)
    
    def __authenticate(self, **kwargs) -> None:
    
        #################################################################
        ######FAKED FOR NOW
        ######HIT DB INSTEAD
        #################################################################
        registered_users = self.__load_registrants()
        
        try:
            header = kwargs['request_type'].split(' ')
            query_pairs = header[1].split('&')
            username = ''
            password = ''
            for query_pair in query_pairs:
                if 'username=' in query_pair:
                    username = remove_http_pluses(query_pair.split('username=')[1])
                if 'password=' in query_pair:
                    password = remove_http_pluses(query_pair.split('password=')[1])
                    
            
            ##############################################
            ######Developer's backdoor
            if username == 'skinnerfan' and password == 'monstastriper':
                self.__client = ServerClient("Developer",
                                             self.__request.session,
                                             authenticated=True)
                return
            
            if username not in registered_users:
                self.__client = None
                return
        
            if password != registered_users[username]:
                self.__client = None
                return
            
            self.__client = ServerClient(username,
                                         self.__request.session,
                                         authenticated=True)
        except ValueError:
            self.__client = None
    
    def __load_registrants(self) -> Dict:
        registrants = {}
        for user in open(self.__config.USER_DB, 'rt'):
            user_pass = user.split('~')
            registrants[user_pass[0].strip()] = user_pass[1].strip()
        
        return registrants
    
    @property
    def client(self) -> ServerClient:
        return self.__client
    
    @property
    def success(self) -> bool:
        if self.__client is None:
            return False
        
        return self.__client.isauthenticated
    
if __name__ == '__main__':
    # def func():
    #     try:
    #         raise Exception()
    #     except:
    #         return
    #     finally:
    #         print('in finally')
    
    # func()
    
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