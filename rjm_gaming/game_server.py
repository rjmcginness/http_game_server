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
from game_utilities import DataAccess
from game_utilities import FileDataAccess
from game_base import Player


class ServiceClosedError(RuntimeError):
    pass

class ServerClientService(Thread):
    def __init__(self, config: Config) -> None:
        super().__init__() # have to call this in __init__ of Thread subclass
        self.__config = config
        self.__client_id = None
        self.__client = None
        self.__requests = []
        self.__exit = False
        
    def run(self):
        ''' If client_id is None, generate and id, embed in html, and
            send the authentication form to user
        '''
        while not self.__exit:
            if not self.__requests:
                continue
            
            #######???POTENTIAL FOR THREAD LOCK OR RACING???
            request = self.__requests.pop(0) # process next request (queue)
            print('REQUEST', request)
            
            if self.__client_id is None:   # authentication form not sent yet
                self.__client_id = request.session.client_id
                self.__send_authentication(request)
                continue
            
            # print("REQUEST:\n", request)
            self.__process_request(request)
    
    def stop(self) -> None: ######???MIGHT WANT TO USE EVENT FOR THIS????
        self.__exit = True
    
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
        '''Distributes the HTTPRequest to the proper CRUD handler'''
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
        if self.__exit:
            raise ServiceClosedError(f'Client has stopped: ID - {self.__client_id}')
            
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
        self.__game = dict(game=None, view=None)
        self.start()
    
    def get(self, **kwargs) -> None:
        ''' Process GET request to GameServer'''
        ######TODO: MAKE MORE ROBUST BY ROUTING UNRECOGNIZED REQUESTS
        ######to safety
        request_type = kwargs['request_type']
        action = self.__parse_path(request_type)
        
        
        if action == '/' or action == '/auth':
            if self.client is None: # no authenticated client
                # run authenticator to authenticate client
                authenticator = Authenticator(self.config, **kwargs)
                
                if not authenticator.success:
                    print('AUTHENTICATION FAILED')
                    self.__client_id = None # Have to resend form
                    return
            
                self._ServerClientService__client = authenticator.client
                print(f'User Authenticated:\n{self.client.name} ({self.client.client_id}) has entered')
                return
            else: 
                action = '/menu' # go to main menu
        
        # if here, there is an authenticated client
        
        request = kwargs['request']
        
        # send main menu
        if action == '/menu':
            self.__send_main_menu(request)
            
            return
        
        # send games menu
        if action == '/games':
            self.__send_games_menu(request)
            return
        
        # loads and sends start page for game
        if action == '/game':
            game_name = self.__parse_input(request_type).lower() ######???DO I NEED LOWER CASE???
            self.__game = self.__engine.load_game(game_name)
            self.__game['game'].add_player(Player(self.client.name, self.__client_id()))
            request.connect.render(self.__game['view'].introduction())
            return
        
        if self.__game['game'] is not None and action == '/game/' + self.__game['game'].name:
            kwargs = self.__game['view'].get_play(request)
            result = self.__game['game'].play_next(**kwargs)
            response = dict(session=HTTPSession(self.__client_id), result=result)
            
            self.__game['view'].render(**response)
            return
        
        # send admin menu
        if action == '/admin':
            self.__send_admin_menu(request)
            return
        
        # exit and close this service
        if action == '/exit': # kill the client
            self._ServerClientService__client = None
            self.__client_id = None
            self.stop()
            return
            
    
    def put(self, **kwargs) -> None:
        print("IMPLEMENT PUT")

    def post(self, **kwargs) -> None:
        print("IMPLEMENT POST")
    
    def delete(self, **kwargs) -> None:
        print("IMPLEMENT DEL")
    
    def error(self, **kwargs) -> None:
        print("IMPLEMENT ERROR")
        
    def __read_output_file(self, file_name: str) -> str:
        '''SIMPLY READS IN WHOLE FILE AND RETURNS AS STRING'''
        html = ''
        with open(self.config.MENU_FILE, 'rt') as menu_file:
            html = menu_file.read()
        
        return html
    
    def __parse_path(self, request_type: str) -> str:
        action = request_type.split(' ')[1].strip() # second section of request type line
        end_idx = action.rfind('?')
        action = action[:end_idx]
        
        return action
    
    def __prep_output_file(self, output_file: str, request: HTTPRequest) -> str:
        '''Embeds session (client_id) in output, if there is a session'''
        ######TODO: Consider checking whether this is a form, if not, add
        ######cookie with client id (session) to response header
        if not request.session:
            return output_file
        
        return request.session.form_insert(output_file)
        
    def __send_main_menu(self, request: HTTPRequest) -> None:
        
        ######SEEMS LIKE THIS PARADIGM MAY BE NICE FOR A DECORATOR
        ######SEE ServerClientService_send__authentication also
        header = HTTPHeader()
        # header.set_cookie = f'cookie1={request.session}'
        header.content_type = 'text/html; charset=utf-8'
        
        # load main menu and prepare with session, if present
        main_menu = self.__read_output_file(self.config.MENU_FILE)
        main_menu = self.__prep_output_file(main_menu, request)
        
        header.content_length = str(len(main_menu))
        
        request.connection.render(main_menu, header=header)
    
    def __parse_input(self, request_type: str) -> str:
        ''' Get the input value from request.
            Returns the value as a string, if present.
            Otherwise, returns None.
        '''
        query = request_type.split(' ')[1]
        sections = query.split('&')
        
        input_value = None
        for section in sections:
            if 'input=' in section:
                idx = section.index('input=')
                input_value = section[idx + len('input=')]
        
        return input_value
    
    def __send_games_menu(self, request: HTTPRequest) -> None:
        
        header = HTTPHeader()
        header.content_type = 'text/html; charset=utf-8'
        
        games_menu = self.__read_output_file(self.config.MENU)
        
        game_names = self.__engine.get_games()
        
        games_html = ''
        for name in game_names:
            games_html += self.__build_game_html(name)
            
        games_menu = games_menu.replace('%GAMES%', games_html)
        
        # prep file after adding game html
        games_menu = self.__prep_output_file(games_menu, request)
        
        header.content_length = len(games_menu)
        
        request.connection.render(games_menu, header=header)
        
    
    def __build_game_html(self, game_name: str) -> str:
        game_link = '<form action="/game" method="get">'
        game_link += f'<input type="submit" value="{game_name}" name="game" />'
        game_link += '</form>'
        
        return game_link

    def __send_admin_menu(self, request: HTTPRequest) -> None:
        print("NOT IMPLEMENTED")
        ######SEND BACK MAIN MENU FOR NOW
        self.__send_main_menu(request)
        
    

class GameServer:######Consider implementing as ContextManager
    def __init__(self, address: str = 'localhost',
                       port: int = 6500,
                       data_access: DataAccess = \
                       FileDataAccess('../init/game_init.i', raw=False)) -> None:
        
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create server
        self.__clients = {}
        self.__engine = GameEngine(data_access)
        self.__server.bind((address, port))
        self.__server.listen(5)
        print(f'Starting server on {port}...')
        
    def start(self) -> None:
        with self.__server as server:
            try:
                while True:
                    connection, address = server.accept() # receive new socket connection
                    print("New Connection:", connection)
                    RequestRouter(connection, self) # route connection to client
                    ######UPGRADE: Time frequency of accepts, spawn new server (load balancing)
            except (ConnectionAbortedError,
                    KeyboardInterrupt,
                    SystemExit) as e:
                stderr.write("Server closing...\n" + str(e) + str(time.ctime()))
                self.shutdown()
                raise
            
    def shutdown(self):
        for client in self.__clients.values():
            client.stop()
        self.__server.close()
        
    @property
    def clients(self) -> Dict:
        return self.__clients.copy()
    
    def create_client(self, request: HTTPRequest) -> None:
        ''' Create a new Game service and push this request
            to it.
        '''
        service = GameClientService(Config(), self.__engine)
        self.__clients[request.session.client_id] = service
        print('New Game Client Service created')
        service.push(request)


class RequestRouter(Thread):
    def __init__(self, connection: socket.socket, server: GameServer) -> None:
        super().__init__()
        self.__connection = connection
        self.__server = server
        self.start()
    
    def run(self): # implement this as thread task.  Called after Thread.start
        ''' Create HTTPRequest object with the socket connection, which
            reads the HTTP request from the client.  Calls method to route
            this request to the correct client, based on client id (session).
        '''
        request = HTTPRequest(self.__connection)
        print('IN REQUESTROUTER', request)
        
        if not request.session: # no session, so make a new one
            request.session = HTTPSession(request.name + str(time.time()))
            print(request.session)
        self.route_request(request)
    
    def route_request(self, request: HTTPRequest) -> None:
        ''' Routes the HTTPRequest to proper client or has
            the server create an new client and routes the
            request to it.
        '''
        try:
            client_id = request.session.client_id
            self.__server.clients[client_id].push(request)
        except ServiceClosedError as e:
            print(e)
            del self.__server_clients[client_id]
        except KeyError:
            # KeyError: client not found
            # AttribiteError: session should never be None
            self.__server.create_client(request)######MAY HAVE TO LOCK ON THIS
    



if __name__ == '__main__':
    from sys import exit
    
    def close_server():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(('localhost', 6500))
            print("Closing server")
            server.close()
            print("Closed")
            from sys import exit
            exit()
            
    close_server()
    
    # from game_utilities import FileDataAccess
    
    # fa = FileDataAccess('../init/game_init.i', raw=False)
    # fa.initialize()
    
    # engine = GameEngine(fa)
    # engine.load_game('Quiz')
    
    # service = GameClientService(Config(), engine)
    
    
    
    # service.stop()
    
    # server = None
    # try:
    #     server = GameServer()
    #     print("ctrl+c to exit")
    #     server.start()
    # except (ConnectionAbortedError, KeyboardInterrupt) as e:
    #     print(e)
    #     server.shutdown()
    #     print('Closing server...')
    #     exit()
    
    # from game_utilities import FileDataAccess
    
    # fa = FileDataAccess('../init/game_init.i', raw=False)
    # fa.initialize()
    
    # engine = GameEngine(fa)
    # engine.load_game('Quiz')
    try:
        print('Starting server...')
        server = GameServer()
        server.start()
    except Exception as e:
        print(e)
        exit()
    finally:
        server.shutdown()
        
    
    
    # try:
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    #         try:
    #             server.bind(('localhost', 6500))
    #             server.listen(5)
    #             print("Server started @6500")
    #             connection, address = server.accept()
    #             request = HTTPRequest(connection)
    #             request.session = HTTPSession(request.name + str(time.time()))
    #             # print(connection.recv(2048))
    #             # print(connection)
                
    #             client = GameClientService(Config(), engine)
    #             client.push(request)
                
    #             connection, address = server.accept()
    #             request = HTTPRequest(connection)
    #             client.push(request)
                
    #             # auth = Authenticator(comms, Config())
    #             # if auth.success:
    #             #     print(auth.client)
    #         finally:
    #             server.close()
    # finally:
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
   