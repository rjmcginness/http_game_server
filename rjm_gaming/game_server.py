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
        ''' If client_id is None, generate an id, embed in html, and
            send the authentication form to user
        '''
        while not self.__exit:
            if not self.__requests:
                continue
            
            #######???POTENTIAL FOR THREAD LOCK OR RACING???
            request = self.__requests.pop(0) # process next request (queue)
            
            if self.__client_id is None:   # authentication form not sent yet
                self.__client_id = request.session.client_id
                self.__send_authentication(request)
                continue
            
            # print("REQUEST:\n", request)
            self.__process_request(request)
    
    def stop(self) -> None: ######???MIGHT WANT TO USE EVENT FOR THIS????
        for request in self.__requests:
            request.connection.close() 
        self.__exit = True
    
    def __send_authentication(self, request: HTTPRequest) -> None:
        ''' Generates and sends the authentication page response to 
            initial GET for accessing server @ '/'
        '''
        header = HTTPHeader()
        header.content_type = 'text/html; charset=utf-8' # sending html
        header.connection = 'keep-alive' # NEED THIS< BECAUSE OF FAVICON
        # header.cache_control = 'no-cache'
        
        client_id = request.session.client_id
        session = HTTPSession(client_id) # new session with client_id
        
        login_form = session.form_file_insert(self.__config.LOGIN_FORM)
        header.content_length = str(len(login_form)) # include dynamic content length of html 
        
        
        request.connection.render(login_form, header=header)
        request.connection.hunt_and_kill_favicon()
        request.mark_complete()
        
        
    
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
    def client_id(self) -> str:
        return self.__client_id
    
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
        
        request = kwargs['request']
        
        # authenticate or send main menu page
        # if action == '/' or action == '/auth':
        if action == '/auth':
            if self.client is None: # no authenticated client
                if not self.__authenticate(**kwargs):
                    self.__send_login_failed(request)
                    return
                
            action = '/menu' # go to main menu
        
        # if here, there is an authenticated client
        
        # send main menu
        if action == '/menu':
            
            # self.__kill_favicon(request)
            self.__send_main_menu(request)
            return
        
        # send games menu
        if action == '/games':
            self.__send_games_menu(request)
            return
        
        # loads and sends start page for game
        if action == '/game':
            game_name = self.__parse_query(request_type, 'game=')
            print(f'Starting {game_name}')
            self.__game = self.__engine.load_game(game_name)
            self._ServerClientService__client = Player(self.client.name, self.client_id)
            self.__game['game'].add_player(self.client)
            kwargs['player'] = self.client
            header = HTTPHeader()
            header.content_type = 'text/html; charset=utf-8'
            header.connection = 'close'
            header.cache_control = 'no-cache'
            
            output = self.__game['view'].introduction(**kwargs)
            header.content_length = len(output)
            
            request.connection.render(output, header=header)
            return
        
        # send a game page: should be called when message sent back from game screen
        if self.__game['game'] is not None and action == '/game/' + self.__game['game'].name.lower():
            kwargs = self.__game['view'].get_play(request.request_type)
            print()
            print(kwargs)
            print()
            result = self.__game['game'].play_next(**kwargs)
            kwargs = dict(session=HTTPSession(self.client_id),
                            game_result=result)
            
            reponse = self.__game['view'].render(**kwargs) # use GameView to render output
            
            header = HTTPHeader()
            header.content_type = 'text/html; charset=utf-8'
            header.cache_control = 'no-cache'
            header.connection = 'close'
            header.content_length = len(reponse)
            
            request.connection.render(reponse, header=header)
            return
        
        # send admin menu
        if action == '/admin':
            self.__send_admin_menu(request)
            return
        
        # exit and close this service
        if action == '/exit': # kill the client
            self.__send_exit(request)
            self._ServerClientService__client = None
            self.__client_id = None
            return
        
        header = HTTPHeader()
        header.connection = 'close'
        header.content_length = 0
        request.connection.render('', header=header, status_code=404)
            
    
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
        with open(file_name, 'rt') as menu_file:
            html = menu_file.read()
        
        return html
    
    def __authenticate(self, **kwargs) -> bool:
        ''' Use Authenticator object to authenticate client
            Return True on success, False on failure
        '''
        # run authenticator to authenticate client
        authenticator = Authenticator(self.config, **kwargs)
        
        if not authenticator.success:
            print('AUTHENTICATION FAILED')
            self._ServerClientService__client_id = None # this will cause authentication to be resent in base class
            return False
    
        self._ServerClientService__client = authenticator.client
        print(f'User Authenticated:\n{self.client.name} ({self.client.client_id}) has entered')
        
        return True
        
    
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
    
    def __send_login_failed(self, request: HTTPRequest) -> None:
        ''' User credentials not authenticated. Send page telling client
            that has a link back to login page.
        '''
        header = HTTPHeader()
        header.content_type = 'text/html; charset=utf-8'
        header.connection = 'close'
        
        login_fail_file = self.__read_output_file(self.config.LOGIN_FAIL)
        
        # following adds session info to page
        login_fail_file = self.__prep_output_file(login_fail_file, request)
        
        header.content_length = len(login_fail_file)
        
        request.connection.render(login_fail_file, header=header)
        
    def __send_main_menu(self, request: HTTPRequest) -> None:
        
        ######SEEMS LIKE THIS PARADIGM MAY BE NICE FOR A DECORATOR
        ######SEE ServerClientService_send__authentication also
        header = HTTPHeader()
        # header.set_cookie = f'cookie1={request.session}'
        header.content_type = 'text/html; charset=utf-8'
        header.connection = 'close' # could make these smarter by parsing for text/css, etc
        
        # load main menu and prepare with session, if present
        main_menu = self.__read_output_file(self.config.MENU_FILE)
        main_menu = self.__prep_output_file(main_menu, request)
        
        header.content_length = str(len(main_menu))
        
        request.connection.render(main_menu, header=header)
    
    def __parse_query(self, request_type: str, name: str) -> str:
        ''' Get the input value from request.
            Returns the value as a string, if present.
            Otherwise, returns None.
        '''
        query = request_type.split(' ')[1]
        sections = query.split('&')
        
        input_value = None
        for section in sections:
            if name in section:
                idx = section.index(name)
                input_value = section[idx + len(name):]
                break
        
        return input_value
    
    def __send_games_menu(self, request: HTTPRequest) -> None:
        
        header = HTTPHeader()
        header.content_type = 'text/html; charset=utf-8'
        header.connection = 'close'
        
        games_menu = self.__read_output_file(self.config.GAME_MENU)
        
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
    
    
    def __send_exit(self, request: HTTPRequest) -> None:
        header = HTTPHeader()
        header.content_type = 'text/html; charset=utf-8'
        header.connection = 'close'
        
        exit_page = self.__read_output_file(self.config.EXIT)
        
        header.content_length = len(exit_page)
        
        request.connection.render(exit_page, header=header)
        
    

class GameServer:######This Should be a thread, so that it can be shutdown
    def __init__(self, address: str = 'localhost',
                       port: int = 6500,
                       data_access: DataAccess = \
                       FileDataAccess('../init/game_init.i', raw=False)) -> None:
        
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create server
        self.__clients = {}
        self.__engine = GameEngine(data_access)
        self.__server.bind((address, port))
        self.__server.listen(5)
        print(f'Server started on {port}')
        
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
                stderr.write("Server closing...\n" + str(e) + str(time.ctime()) + '\n')
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
        
        if not request.session: # no session, so make a new one
            request.session = HTTPSession(request.name + str(time.time()))
            
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
            del self.__server.clients[client_id]
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
        server.shutdown()
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

'''
Exception in thread Thread-115:
Traceback (most recent call last):
  File "/opt/anaconda3/lib/python3.9/threading.py", line 973, in _bootstrap_inner
    self.run()
  File "/Users/robertjmcginness/src/pyth/rjm_games_2_0/rjm_gaming/game_server.py", line 57, in run
    self.__process_request(request)
  File "/Users/robertjmcginness/src/pyth/rjm_games_2_0/rjm_gaming/game_server.py", line 91, in __process_request
    self.get(**kwargs)
  File "/Users/robertjmcginness/src/pyth/rjm_games_2_0/rjm_gaming/game_server.py", line 208, in get
    result = self.__game['game'].play_next(**kwargs)
  File "/Users/robertjmcginness/src/pyth/rjm_games_2_0/rjm_gaming/game_base.py", line 226, in play_next
    result = self._next_result(**kwargs)
  File "/Users/robertjmcginness/src/pyth/rjm_games_2_0/games/quiz.py", line 211, in _next_result
    question_num=self.__current_submission.question.q_id,
AttributeError: 'NoneType' object has no attribute 'question'
'''
        
        
        
        
  
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

'''
HTTPCommsModule.READ ('127.0.0.1', 57570)
REQUEST GET /favicon.ico HTTP/1.1
Host: localhost:6500
Connection: keep-alive
sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"
sec-ch-ua-mobile: ?0
User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36
sec-ch-ua-platform: "Windows"
Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: no-cors
Sec-Fetch-Dest: image
Referer: http://localhost:6500/games?input=Games&identifier=575201652452595.659528
Accept-Language: en-US,en;q=0.9,is;q=0.8,de;q=0.7,da;q=0.6
Accept-Encoding: gzip, deflate
'''
   