# -*- coding: utf-8 -*-
"""
Created on Tue May  3 10:08:07 2022

@author: Robert J McGinness
"""

import socket
from typing import Tuple
from typing import Any

from game_utilities import CommsModule
from game_utilities import GameCommsError
from game_utilities import CommRegistrant


class GameSocket(CommRegistrant):
    def __init__(self, game_socket: socket.socket, address: Tuple) -> None:
        self.__socket = game_socket
        self.__address = address
    
    def read(self) -> Any:
        return 
    
    def write(self, data: Any) -> None:
        total_sent = 0
        while total_sent < len(data):
            sent = self.__socket.send(bytes(str.encode(data)))
            if sent == 0:
                raise GameCommsError(f"Incomplete data sent to client @{self.__address}")
            print(bytes(data.encode()))
            total_sent += sent
        #self.__socket
    
    def close(self) -> None:
        self.__socket.close()
    
    def __repr__(self) -> str:
        return f"socket={self.__socket} at address={self.__address}"
    


class AsyncCommsModule(CommsModule):
    def __init__(self, max_clients: int = 1) -> None:
        super().__init__()
        self.__max_connections = max_clients
    
    def write(self, data: Any) -> Any:
        message = "HTTP/1.1 200 OK\nContent-Type: text/html\n\r\n"
        message += "<!DOCTYPE html><head></head><html><body>Hello, World!</body></html>"
        self._CommsModule__io[0].write(message)
    
    def read_input(self) -> Any:
        pass
    
    def display(self, data: Any) -> Any:
        pass
    
    def unregister(self, game_socket: GameSocket) -> None:
        if game_socket in self._CommsModule__io:
            game_socket.close()
            self._CommsModule__io.remove(game_socket)
    
    def unregister_all(self) -> None:
        for game_socket in self._CommsModule__io:
            game_socket.close()
            self._CommsModule__io.remove(game_socket)
        
        
if __name__ == '__main__':
    import sys
    sys.exit()
    