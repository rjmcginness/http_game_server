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
    
    """ favicon_kill_tester.py works by having the browser check for
        favicon.ico every time and sending 404 or timing out.
        
        Instead of having to use this after every communication,
        favicon_kill_tester2.py will investigate whether you
        you can send 404 on the first request by the browser
        for favicon.ico, then not worrying about it.  That way
        the server can handle requests for css and scripts.
        
        THIS ALSO WORKS, but it assumes that favicon will be cached
        and not requested again
        
        The final thing to test is what is being fetched by the
        browser, ie. favicon.ico, css, js, image, whatever.
    """
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
        got_favicon = False
        
        while True:
            connection, address = server.accept()
            print("CONN:", connection, address)
            print()
            
            request = connection.recv(2048).decode()
            print('First Request:', request)
            print()
            print()
            data_sent = 0
            while data_sent < len(html):
                data_sent += connection.send(html)
            
            connection.settimeout(1)
            try:
                request = connection.recv(2048).decode()
                if '/favicon' in request:
                    favicon_killer = 'HTTP/1.1 404\nConnection: close\n\r\n'
                    
                    favicon_killer = bytes(favicon_killer.encode('utf-8'))
                    
                    # connection.sendall(favicon_killer)
                    
                    data_sent = 0
                    while data_sent < len(favicon_killer):
                        data_sent += connection.send(favicon_killer)
                        print('kill favicon')
                    got_favicon = True
                print('SECOND REQUEST:', request)
                    
            except socket.timeout:
                pass
            finally:
                connection.close()
                    
            
            
            
            
                
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
    finally:
        server.close()
            