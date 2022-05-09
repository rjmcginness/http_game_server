#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  6 18:54:52 2022

@author: robertjmcginness
"""

import socket
from threading import Thread
# import http
from typing import Dict
import time
from sys import stderr

from game_server import GameClientService
from config import Config

class HTTPRequest:
    def __init__(self, connection: socket.socket, request: str) -> None:
        self.__connection = connection
        self.__request = request
    
    @property
    def connection(self) -> socket.socket:
        return self.__connection
    
    @property
    def request(self) -> str:
        return self.__request
    
    def __repr__(self) -> str:
        return self.__request

class GameServer(Thread):######FAKED FOR TESTING
    def __init__(self) -> None:
        
        super().__init__()
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__clients = {}
        self.__server.bind(('localhost', 6500))
        self.__server.listen(1)
        
    def run(self) -> None:
        with self.__server as server:
            while True:
                try:
                    connection, address = server.accept()
                    print("New Connection:", connection)
                    RequestRouter(connection, self)
                    ######UPGRADE: Time frequency of accepts, spawn new server (load balancing)
                except (KeyboardInterrupt, SystemExit) as e:
                    stderr.write("Server closing", e, address, time.time())
                    raise
            self.shutdown()
        
        ######Consider an event to shudown thread
    
    def shutdown(self):
        super().__exit__()
        print("Closing clients")
        for client in self.__clients.values():
            client.dispatch()
        
    @property
    def clients(self) -> Dict:
        return self.__clients.copy()
    
    def create_client(self, request: HTTPRequest) -> None:
        connection = request.connection
        client_id = str(connection.getsockname()[1]) + str(time.time())
        print(client_id)
        
        ######CREATE SERVICE: No Engine for testing
        service = GameClientService(Config(), connection, None)
        print('New Game Client Service created')
        service.push(request)
        self.__clients[client_id] = service
        
        
class RequestRouter(Thread):
    def __init__(self, connection: socket.socket, server: GameServer) -> None:
        
        super().__init__()
        self.__connection = connection
        self.__server = server
        self.start()
    
    def run(self):
        request = HTTPRequest(self.__connection,
                              self.__connection.recv(2048).decode())
        self.route_request(request)
    
    def route_request(self, request: HTTPRequest) -> None:
        try:
            client = self.__determine_client(request)
            self.__server.clients[client].push(request)
        except KeyError:
            self.__server.create_client(request)######MAY HAVE TO LOCK ON THIS
    
    def __determine_client(self, request: HTTPRequest) -> str:
        ''' Returns the session identifier in an HTTPRequest.
            Parses for the tag <input hidden type="password" 
            value="IDENTIFIER"/>, where IDENTIFIER is the session ID
            
            Returns the session identifier value, if found, or None
        '''
        try:
            found_at_idx = request.request.index('name="identifier"')
            identifier_idx = request.request[found_at_idx:].find('value=')
            identifier_idx += len('value=') + 1
            end_idx = request.request[identifier_idx].find('"')
            return request.request[identifier_idx:end_idx]
        except ValueError:
            print("IDENTIFIER NOT FOUND")
        
        return None
            
    # def __tag(self, request) -> str:
    #     return '<input hidden type="password" value=""/>'######FIX: NEED VALUE
    
if __name__ == '__main__':
    # from sys import exit
    
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM)as server:
    #     server.bind(('localhost', 6500))
    #     server.close()
    #     print("Closing")
    
    # print("Closed")
    # exit()
    try:
        server = GameServer()
        print("Starting GameServer... @6500")
        server.start()
    except KeyboardInterrupt:
        print("Shut down...")
        raise
    
    # socket_list = []
    
    # try:
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    #         server.bind(('localhost', 6510))
    #         server.listen(1)
    #         while True:
    #             socket_list.append(server.accept())
    #             print(socket_list[-1])
    # except (KeyboardInterrupt, SystemExit) as e:
    #     print(e)
    #     raise 
    # finally:
    #     print('in finally')
    #     print([sock[0].close() for sock in socket_list])
    #     server.close()