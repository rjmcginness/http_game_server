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
            
class GameClientService(ServerClientService):
    def __init__(self, config: Config, comms: HTTPCommsModule, engine: GameEngine):
        super().__init__(config, comms)
        self.__engine = engine
        self.__player
    
    def run(self):
        super().run()
        
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
    server = GameServer('localhost', port=5550, max_connect_requests=5)
    game_socket = next(server.watch())
    
    a_comms = HTTPCommsModule()
    a_comms.register_output(game_socket)
    
    game_names = []
    # game_row = '<tr><td>.name</td><td><form action=".name" method="get"><button type="button" value=".name" action="War" method="get">Play</button></form></td></tr>'
    # game_row = '<tr><td>.name</td><td><form action=".name" method="get"><input type="submit" value="Play" method="get"/></form></td></tr>'
    game_row = '<tr><td><a href="/.name">Play .name</a></td></tr>'
    game_rows = ''
    
    with open('game_init.i', 'rt') as init_file:
        for game_init in init_file:
            game_names.append(game_init.split()[0])
            game_rows += game_row.replace('.name', game_names[-1].strip())
    
    output_str = "HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8\n\r\n"
    with open('../static/menu.html', 'rt') as templ:
        for line in templ:
            output_str += line.strip()
    
    output_str = output_str.replace('GAMES', game_rows)
    
    content = ''
    with open('../static/css/menu.css', 'rt') as css_file:
        for line in css_file:
            content += line.strip()
    
    output_str = output_str.replace('</head>', f'<style>{content}</style></head>')
    
    a_comms.write(output_str)
    
    while (request := a_comms.read_input()):
        print('REQUEST', request)

    print('REQUEST', request)
    #output_str = '200 OK\nContent-Type: text/css; charset=utf-8\n'
    
    # content = ''
    # with open('../static/css/menu.css', 'rt') as css_file:
    #     for line in css_file:
    #         content += line.strip()
    
    # output_str += f'Content-Length: {len(content)}\n'
    
    
    # a_comms.write(output_str + content + '\r\n')
    # print(output_str+ content + '\r\n')
    #a_comms.write(output_str + content + '\r\n')
    
    input('Press enter to stop server')
   