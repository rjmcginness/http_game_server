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
        super().__init__() # have to call this in __init__ of Thread subclass
        self.__config = config
        self.__client_id = None
        self.__client = None
        self.__requests = []
        
    def run(self):
        ''' If client_id is None, generate and id, embed in html, and
            send the authentication form to user
        '''
        while True:
            if not self.__requests:
                continue
            #######???POTENTIAL FOR THREAD LOCK OR RACING???
            request = self.__requests.pop(0) # process next request
            
            if self.__client_id is None:   # authentication form not sent yet
                self.__client_id = request.session.client_id
                self.__send_authentication((request))
                continue
            
            # print("REQUEST:\n", request)
            self.__process_request(request)
    
    def __send_authentication(self, request: HTTPRequest) -> None:
        ''' Generates and sends the authentication page response to 
            initial GET for accessing server @ '/'
        '''
        header = HTTPHeader()
        header.content_type = 'text/html; charset=utf-8' # sending html
        
        client_id = request.session.client_id
        session = HTTPSession(client_id) # new session with client_id
        
        login_form = session.form_file_insert(self.__config.LOGIN_FORM)
        header.content_length = str(len(login_form)) # include dynamic content length of html 
        
        request.connection.render(login_form, header=header)
    
    def __process_request(self, request: HTTPRequest) -> None:
        
        kwargs = dict(request=request, request_type=request.request_type,
                                          header=request.header,
                                          body=request.body)
        
        crud_line = request.request_type.lower()
            
        #PROCESS CRUD REQUEST: EACH OF THESE IMPLEMENTED IN SUBCLASS
        if 'get' in crud_line:
            self.get(**kwargs)
        elif 'put' in crud_line:
            self.put(**kwargs)
        elif 'post' in crud_line:
            self.post(**kwargs)
        elif 'delete' in crud_line:
            self.delete(**kwargs)
        else:
            self.error(request=request)
    
    def push(self, request: Any) -> None:
        '''New request from this client'''
        if request is None:
            return
        
        self.__requests.append(request)
    
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
            
class GameClientService(ServerClientService):
    def __init__(self, config: Config, engine: GameEngine):
        super().__init__(config)
        self.__engine = engine
        self.__player_id = ''#######FIX This 
        self.start()
    
    def get(self, **kwargs) -> None:
        
        if self.client is None:
            # run authenticator to authenticate client
            authenticator = Authenticator(self.config, **kwargs)
            
            if not authenticator.success:
                print('AUTHENTICATION FAILED')
                self.__client_id = None # Have to resend form
                return

            self._ServerClientService__client = authenticator.client
            print(f'User Authenticated:\n{self.client.name} ({self.client.client_id}) has entered')
            self.__send_main_menu(kwargs['request'])
    
    def put(self, **kwargs) -> None:
        print("IMPLEMENT PUT")

    def post(self, **kwargs) -> None:
        print("IMPLEMENT POST")
    
    def delete(self, **kwargs) -> None:
        print("IMPLEMENT DEL")
    
    def error(self, **kwargs) -> None:
        print("IMPLEMENT ERROR")
        
    def __send_main_menu(self, request: HTTPRequest) -> None:
        
        ######SEEMS LIKE THIS PARADIGM MAY BE NICE FOR A DECORATOR
        ######SEE ServerClientService_senf__authentication also
        header = HTTPHeader()
        header.set_cookie = f'cookie1={request.session}'
        header.content_type = 'text/html; charset=utf-8'
        
        main_menu = request.session.form_file_insert(self.config.MENU_FILE)
        
        header.content_length = str(len(main_menu))
        
        request.connection.render_file(main_menu, header=header)
    

class GameServer:######Consider implementing as ContextManager
    def __init__(self, address: str = 'localhost', port: int = 6500) -> None:
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__clients = {}
        self.__server.bind((address, port))
        self.__server.listen(5)
        print(f'Starting server on {port}...')
        
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
                stderr.write("Server closing...\n" + str(e) + str(time.ctime()))
                self.shutdown()
                raise
            
    def shutdown(self):
        self.__server.close()
        
    @property
    def clients(self) -> Dict:
        return self.__clients.copy()
    
    def create_client(self, request: HTTPRequest) -> None:
        ''' Create a new Game service and push this request
            to it.
        '''
        ######CREATE SERVICE: No Engine for testing
        service = GameClientService(Config(), None) # could gave session as constructor argument 
        self.__clients[request.session.client_id] = service
        print('New Game Client Service created')
        service.push(request)


class RequestRouter(Thread):
    def __init__(self, connection: socket.socket, server: GameServer) -> None:
        super().__init__()
        self.__connection = connection
        self.__server = server
        self.start()
    
    def run(self):
        request = HTTPRequest(self.__connection)
        
        if not request.session: # no session, so make a new one
            request.session = HTTPSession(request.name + str(time.time()))
        self.route_request(request)
    
    def route_request(self, request: HTTPRequest) -> None:
        try:
            client_id = request.session.client_id
            self.__server.clients[client_id].push(request)
        except KeyError:
            # KeyError: client not found
            # AttribiteError: session should never be None
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
    server = None
    try:
        server = GameServer()
        print("ctrl+c to exit")
        server.start()
    except (ConnectionAbortedError, KeyboardInterrupt) as e:
        print(e)
        server.shutdown()
        print('Closing server...')
        exit()
        
        
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
   