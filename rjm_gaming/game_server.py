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
    a_comms.unregister(game_socket)#########closes socket (may not want to close it, as it may be transferred to another game)
    for sock in a_comms.connections:
        sock.close()