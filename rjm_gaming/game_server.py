# -*- coding: utf-8 -*-
"""
Created on Tue May  3 11:17:46 2022

@author: rmcginness
"""

import socket
from sys import exit

from game_utilities import GameCommsError
from game_network import GameSocket
from game_network import AsyncCommsModule

class GameServer:
    def __init__(self, server_address: str, port: int = 5550,
                                     max_connect_requests: int = 1) -> None:
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.__server.bind((server_address, port))
        print('Starting server at', f'{self.__server.getsockname()}')
        self.__server.listen(max_connect_requests)
    
    def watch(self) -> GameSocket:
        try:
            while True:
                clientsocket, address = self.__server.accept()
                print(f"connected to {address}")
                yield GameSocket(clientsocket, address)
                break
        except KeyboardInterrupt:
                print('Exiting server...')
                exit()
        except Exception as e:
            raise GameCommsError from e
        finally:
            self.__server.close()
        
        return

if __name__ == '__main__':
    server = GameServer('localhost', port=5550, max_connect_requests=5)
    game_socket = next(server.watch())
    
    a_comms = AsyncCommsModule()
    a_comms.register_output(game_socket)
    
    game_names = []
    game_row = '<tr><td>.name</td><td><button type="button" name=".name">Play</button></td></tr>'
    
    with open('game_init.i', 'rt') as init_file:
        for game_init in init_file.readline():
            game_names.append(game_init.split()[0])
    
    output_str = "HTTP/1.1 200 OK\nContent-Type: text/html\n\r\n"
    with open('../static/menu.html', 'rt') as templ:
        output_str += templ.read()
    
    output = output.replace('GAMES', game_rows)
    
    a_comms.write(None)
    a_comms.unregister(game_socket)