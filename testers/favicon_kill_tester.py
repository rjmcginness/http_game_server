# -*- coding: utf-8 -*-
"""
Created on Fri May 13 15:31:39 2022


Interesting study on the difficulty
of favicon.ico request


@author: Robert J McGinness
"""

import socket
from sys import exit

if __name__ == '__main__':
    try:
        
        html = 'HTTP/1.1 OK 200\n'
        html = 'HTTP/1.1 200\n'
        html += 'Content-Type: text/html; charset="utf-8"\n'
        
        temp = ''
        with open('favicon_test.html', 'rt') as file:
            temp = file.read()
        
        html += f'Content-Length: {len(temp)}\n\r\n' + temp
        
        html = bytes(html.encode('utf-8'))
        
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', 4100))
        server.listen(5)
        
        while True:
            connection, address = server.accept()
            
            request = connection.recv(2048).decode()
            print('First Request:', request)
            print()
            print()
            data_sent = 0
            while data_sent < len(html):
                data_sent += connection.send(html)
            
            request = connection.recv(2048).decode()
            print('FAVICON REQUEST:', request)
            
            
            favicon_killer = 'HTTP/1.1 404\n\r\n'
            favicon_killer = bytes(favicon_killer.encode('utf-8'))
            
            # connection.sendall(favicon_killer)
            
            data_sent = 0
            while data_sent < len(favicon_killer):
                data_sent += connection.send(favicon_killer)
                print('wrote again')
                
            connection.close()
            
            # request = connection.recv(2048).decode()
            # print('Last Request:', request)
            
            # data_sent = 0
            # while data_sent < len(html):
            #     data_sent += connection.send(html)
            
    except KeyboardInterrupt:
        print('Server closing...')
        server.close()
        exit()
            