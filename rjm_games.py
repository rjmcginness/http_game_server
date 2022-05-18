# -*- coding: utf-8 -*-
"""
Created on Wed May 18 08:38:21 2022

@author: Robert J McGinness
"""

from rjm_gaming.game_server import GameServer


if __name__ == '__main__':
    
    print('Welcome.\n')
    
    address = 'localhost'
    port = ''
    while not port.isdigit():
        try:
            port = input("Please enter port for server: ")
        except TypeError:
            print('Invalid port.  Port number must be a positive integer (use higher numbers)\n')
            port = ''
    
    try:
        print('Starting server...')
        server = GameServer(address, int(port))
        server.start()
    except Exception as e:
        print(e)
        server.shutdown()
        exit()
    finally:
        server.shutdown()

