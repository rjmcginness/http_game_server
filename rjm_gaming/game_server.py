# -*- coding: utf-8 -*-
"""
Created on Tue May  3 11:17:46 2022

@author: rmcginness
"""

import socket
from threading import Thread

from game_network import HTTPCommsModule
from game_network import ServerClient
from game_authentication import Authenticator
from config import Config
from game_engine import GameEngine
from game_utilities import ClassLoader
# from functools import wraps


class ServerClientService(Thread):
    def __init__(self, config: Config, comms: HTTPCommsModule) -> None:
        super().__init__()
        self.__comms = comms
        self.__config = config
        self.__client = None
        
    def run(self):
        authenticator = Authenticator(self.__comms, self.__config)
        if not authenticator.success:
            return
    
        self.__client = authenticator.client
        print(f'{self.client.name} ({self.client.client_id}) has entered')
    
    @property
    def client(self) -> ServerClient:
        return self.__client
    
    @property
    def dispatch(self) -> None:
        self.__comms.close()
    
    @property
    def config(self) -> Config:
        return self.__config
    
    @property
    def comms(self) -> HTTPCommsModule:
        return self.__comms
    
    @abstractmethod
    def get(self, **kwargs) -> None:
        ...
    
    # def get(self, *paths):######decorator????!!!????!!!
    #     def check_get(get_function):
    #         assert not paths is None and len(paths) > 0
            
    #         @wraps(get_function)
    #         def wrapper(*args, **kwargs):
    #             print('Hi')
    #         return wrapper
            
class GameClientService(ServerClientService):
    def __init__(self, config: Config, comms: HTTPCommsModule, engine: GameEngine):
        super().__init__(config, comms)
        self.__engine = engine
        self.__player
        self.start()
    
    def run(self):
        self.get(self.__comms.read())#initial get sent for page
        super().run()#authenticates client
        
        if not self.client:
            return
        
        menu_class = ClassLoader.load_class(self.config.MENU['cls'],
                                            self.config.MENU['module'],
                                            self.config.MENU['package'])
        
        menu = menu_class(self.__comms)
        
        while not menu.exit_requested:
            #########FINISH THIS
            print("IN CLIENT SERVICE LOOP")
            break
        
        self.dispatch()
    
    def get(self, **kwargs) -> None:
    ######I DO NOT LIKE THIS IMPLEMENTATION I WANT IT TO BE SMARTER
    ######get a request, parse for GET, pass to decorated function tha handles
    ######the path/request.  SEE BELOW COMMENTED CODE AS A START
        if 'path' not in kwargs or\
                    kwargs['path'] == '/' or\
                    kwargs['path'] == '':
            menu_class = ClassLoader.load_class(self.config.MENU['cls'],
                                                self.config.MENU['module'],
                                                self.config.MENU['package'])
            
            menu = menu_class(self.__comms)
    
    
    
    # @ServerClientService.get('/menu')
    # def menu(self) -> None:
    #     menu_class = ClassLoader.load_class(self.config.MENU['cls'],
    #                                         self.config.MENU['module'],
    #                                         self.config.MENU['package'])
        
    #     menu = menu_class(self.__comms)
        
    #     while not menu.exit_requested:
    #         #########FINISH THIS
    #         print("IN CLIENT SERVICE LOOP")
    #         break
    

class GameServer:
    def __init__(self, config: Config, server_address: str, port: int = 5550,
                                     max_connect_requests: int = 1) -> None:
        self.__config = config
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__engine = GameEngine(comms)
        
        self.__server.bind((server_address, port))
        print('Starting server at', f'{self.__server.getsockname()}...')
        self.__server.listen(max_connect_requests)
    
    def watch(self) -> GameClientService:
        with self.__server as server:
            # try:
            while True:
                clientsocket, address = server.accept()
                print(f"connected to {address}")
                yield GameClientService(self.__config, HTTPCommsModule(clientsocket),)
                # break
            # except KeyboardInterrupt:
            #         print('Exiting server...')
            #         exit()
            # except SystemExit:
            #     raise
            # except Exception as e:
            #     raise GameCommsError from e
            # finally:
            #     self.__server.close()
        
        return

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('localhost', 6500))
        server.listen(1)
        connection, address = server.accept()
        
        comms = HTTPCommsModule(connection, time_out=None)
        client = GameClientService(Config(), comms, None)
        
        # auth = Authenticator(comms, Config())
        # if auth.success:
        #     print(auth.client)
        
        comms.close()
   