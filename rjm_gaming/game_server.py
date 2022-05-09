# -*- coding: utf-8 -*-
"""
Created on Tue May  3 11:17:46 2022

@author: rmcginness
"""

import socket
import time
from threading import Thread
from abc import abstractmethod
from typing import Any
from typing import Dict
from sys import stderr

from game_network import HTTPRequest
from game_network import HTTPHeader
from game_network import HTTPSession
from game_authentication import Authenticator
from game_authentication import ServerClient
from config import Config
from game_engine import GameEngine
from game_utilities import ClassLoader
# from functools import wraps


class ServerClientService(Thread):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.__config = config
        self.__client_id = None
        self.__client = None
        self.__requests = []
        
    def run(self):
        
        while True:
            if not self.__requests:
                continue
            #######POTENTIAL FOR THREAD LOCK OR RACING???
            request = self.__requests.pop(0)
            if self.__client_id is None:   #nauthentication form not sent yet
                print('Sending authentication...')
                self.__send_authentication((request))
                continue
            
            
            self.__process_request(request)
    
    def __send_authentication(self, request: HTTPRequest) -> None:
        header = HTTPHeader()
        header.content_type = 'text/html; charset=utf-8'
        client_id = request.name + str(time.time())
        session = HTTPSession(client_id)
        login_form = session.form_file_insert(self.__config.LOGIN_FORM)
        print(login_form)
        request.connection.render(login_form)
            
    @property
    def client(self) -> ServerClient:
        return self.__client
    
    @property
    def config(self) -> Config:
        return self.__config
    
    @abstractmethod
    def get(self, **kwargs) -> None:
        ...
    
    @abstractmethod
    def put(self, **kwargs) -> None:
        ...

    @abstractmethod
    def post(self, **kwargs) -> None:
        ...
    
    @abstractmethod
    def delete(self, **kwargs) -> None:
        ...
    
    @abstractmethod
    def error(self, **kwargs) -> None:
        ...
    
    def push(self, request: Any) -> None:
        if request is None:
            return
        
        self.__requests.append(request)
        
        
    def __process_request(self, request: HTTPRequest) -> None:
        request_lines = request.request.split('\n')######WILL THIS WORRK WITH LINUX
        if 'HTTP/1.1' in request_lines[0]:
            crud_line = request_lines[0].lower()
            for idx in range(len(request_lines)):
                if '\n\r\n' in request_lines[idx]:
                    break
            idx += 1
            header = request_lines[1:idx]
            if 'get' in crud_line:
                self.get(request=request,
                         request_type=request_lines[0],
                         header=header,
                         body=request_lines[idx:])
            elif 'put' in crud_line:
                self.put(request=request,
                         request_type=request_lines[0],
                         header=header,
                         body=request_lines[idx:])
            elif 'post' in crud_line:
                self.post(request=request,
                         request_type=request_lines[0],
                         header=header,
                         body=request_lines[idx:])
            elif 'delete' in crud_line:
                self.delete(request=request,
                         request_type=request_lines[0],
                         header=header,
                         body=request_lines[idx:])
            else:
                self.error(request=request)
        
        request.connection.close()
    
    # def get(self, *paths):######decorator????!!!????!!!
    #     def check_get(get_function):
    #         assert not paths is None and len(paths) > 0
            
    #         @wraps(get_function)
    #         def wrapper(*args, **kwargs):
    #             print('Hi')
    #         return wrapper
            
class GameClientService(ServerClientService):
    def __init__(self, config: Config, engine: GameEngine):
        super().__init__(config)
        self.__engine = engine
        self.__player_id = ''#######FIX This 
        self.start()
    
    def get(self, **kwargs) -> None:
    ######I DO NOT LIKE THIS IMPLEMENTATION I WANT IT TO BE SMARTER
    ######get a request, parse for GET, pass to decorated function tha handles
    ######the path/request.  SEE BELOW COMMENTED CODE AS A START
    
        # if 'path' not in kwargs or\
        #             kwargs['path'] == '/' or\
        #             kwargs['path'] == '':
        #     menu_class = ClassLoader.load_class(self.config.MENU['cls'],
        #                                         self.config.MENU['module'],
        #                                         self.config.MENU['package'])
            
        #     menu = menu_class(self.__comms)
        print("REQUEST TYPE:", kwargs['request_type'])
        print("HEADER:", kwargs['header'])
        print("BODY", kwargs['body'])
        request = kwargs['request']
        
        if self.client is None:
            authenticator = Authenticator(self.__config, request)
            time.sleep(2)######hhhmm why?????
            if not authenticator.success:
                self.__client_id = None # Have to resend form
                return

            self.__client = authenticator.client
            print(f'{self.client.name} ({self.client.client_id}) has entered')
        
    
    def put(self, **kwargs) -> None:
        print("IMPLEMENT PUT")

    def post(self, **kwargs) -> None:
        print("IMPLEMENT POST")
    
    def delete(self, **kwargs) -> None:
        print("IMPLEMENT DEL")
    
    def error(self, **kwargs) -> None:
        print("IMPLEMENT ERROR")
    

    
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

class GameServer:######Consider implementing as ContextManager
    def __init__(self, address: str = 'localhost', port: int = 6500) -> None:
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__clients = {}
        self.__server.bind((address, port))
        self.__server.listen(1)
        
    def start(self) -> None:
        with self.__server as server:
            try:
                while True:
                
                    connection, address = server.accept()
                    print("New Connection:", connection)
                    RequestRouter(connection, self)
                    ######UPGRADE: Time frequency of accepts, spawn new server (load balancing)
            except (ConnectionAbortedError,
                    KeyboardInterrupt,
                    SystemExit) as e:
                stderr.write("Server closing...\n" + str(e) + str(time.time()))
                self.shutdown()
                raise
            
        
        ######Consider an event to shudown thread
    
    def shutdown(self):
        self.__server.close()
        
        
    @property
    def clients(self) -> Dict:
        return self.__clients.copy()
    
    def create_client(self, request: HTTPRequest) -> None:
        client_id = request.name + str(time.time())
        print('CLIENT ID:', client_id)
        
        ######CREATE SERVICE: No Engine for testing
        service = GameClientService(Config(), None)
        self.__clients[client_id] = service
        print('New Game Client Service created')
        service.push(request)
        
#########################################################################
######GAMESERVER WAS A THREAD IN IMPLEMENTATION BELOW
#########################################################################

# class GameServer(Thread):######Consider implementing as ContextManager
#     def __init__(self, address: str = 'localhost', port: int = 6500) -> None:
        
#         super().__init__()
#         self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.__clients = {}
#         self.__server.bind((address, port))
#         self.__server.listen(1)
        
#     def run(self) -> None:
#         with self.__server as server:
#             try:
#                 while True:
                
#                     connection, address = server.accept()
#                     print("New Connection:", connection)
#                     RequestRouter(connection, self)
#                     ######UPGRADE: Time frequency of accepts, spawn new server (load balancing)
#             except (ConnectionAbortedError,
#                     KeyboardInterrupt,
#                     SystemExit) as e:
#                 stderr.write("Server closing", e, address, time.time())
#                 self.shutdown()
#                 raise
            
        
#         ######Consider an event to shudown thread
    
#     def shutdown(self):
#         self.__server.close()
#         print("Closing clients")
#         for client in self.__clients.values():
#             client.dispatch()
        
        
#     @property
#     def clients(self) -> Dict:
#         return self.__clients.copy()
    
#     def create_client(self, request: HTTPRequest) -> None:
#         client_id = request.name + str(time.time())
#         print('CLIENT ID:', client_id)
        
#         ######CREATE SERVICE: No Engine for testing
#         service = GameClientService(Config(), None)
#         self.__clients[client_id] = service
#         print('New Game Client Service created')
#         service.push(request)
        
        

class RequestRouter(Thread):
    def __init__(self, connection: socket.socket, server: GameServer) -> None:
        super().__init__()
        self.__connection = connection
        self.__server = server
        self.start()
    
    def run(self):
        request = HTTPRequest(self.__connection)
        self.route_request(request)
    
    def route_request(self, request: HTTPRequest) -> None:
        try:
            client = request.session.client_id
            self.__server.clients[client].push(request)
        except (KeyError, AttributeError):
            # KeyError: client not found
            # AttribiteError: session is None
            self.__server.create_client(request)######MAY HAVE TO LOCK ON THIS
    

def close_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('localhost', 6500))
        print("Closing server")
        server.close()
        print("Closed")
        from sys import exit
        exit()

if __name__ == '__main__':
    # close_server()
    
    from sys import exit
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    #     server.bind(('localhost', 6500))
    #     server.listen(1)
    #     print("Server started")
    #     connection, address = server.accept()
    #     request = HTTPRequest(connection)
    #     # print(connection.recv(2048))
    #     # print(connection)
        
    #     client = GameClientService(Config(), None)
    #     client.push(request)
        
    #     # auth = Authenticator(comms, Config())
    #     # if auth.success:
    #     #     print(auth.client)
    #     server.close()
    server = None
    try:
        server = GameServer()
        print('Starting server...')
        print("ctrl+c to exit")
        server.start()
        server.join()
    except (ConnectionAbortedError, KeyboardInterrupt) as e:
        print(e)
        server.shutdown()
        print('Closing server...')
        exit()
    
        
        
        
        
  
'''GET / HTTP/1.1
Host: localhost:6500
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1'''
   