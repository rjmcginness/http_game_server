# -*- coding: utf-8 -*-
"""
Created on Wed May  4 22:12:38 2022

@author: Robert J McGinness
"""

import threading
import socket
from typing import Tuple

class PlayerConnection:
    def __init__(self, connection: socket.socket, player) -> None:
        self.__connection = connection
        self.__player = player
        
def auth_html():
    output = 'HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8\n\r\n'
    output += '''<!DOCTYPE html>
<html>
<head>
    <meta charset="ut-8"/>
    <title>Login</title>
</head>
<body>
    <form action="/auth" method="put">
        <label for="username">Username:</label>
        <input type="textbox" name="username" value="username"/>
        <label for="pass">Password:</label>
        <input type="password" name="pass" value="pass">
        <input type="submit" value="Login"/>
    </form>
</body>
</html>'''

    return bytes(output.encode('utf-8'))

class Authenticator(threading.Thread):
    def __init__(self, connection: socket.socket) -> None:
        super().__init__()
        self.__connection = connection
        self.__isauthorized = False
        self.__player = None
        self.start()
    
    def __authenticate(self) -> None:
        
        with self.__connection as connection:
            print(connection.recv(1024))
            print(auth_html())
            connection.sendall(auth_html())
            print(connection.recv(1024))
        
        #####HIT DB FOR AUTHENTICATION
        self.__isautorized = True
        self.__player = dict(name="Robert")
    
    def run(self):
        self.__authenticate()
        self.join(5)
    
    @property
    def player(self) -> Tuple:
        return self.__isauthorized, PlayerConnection(self.__connection, self.__player)

if __name__ == '__main__':
    print('Starting server...')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('localhost', 7500))
        server.listen(1)
        connection, address = server.accept()
        # with connection:
        #     # connection.send(bytes('Hello'.encode('utf-8')))
        #     print(connection.recv(1024))
        #     connection.sendall(auth_html())
        #     print("\n\nGET:", connection.recv(1024))
        with connection:
            auth = Authenticator(connection)
            if auth.is_alive():
                auth.join()
    