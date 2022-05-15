# -*- coding: utf-8 -*-
"""
Created on Fri May 13 15:31:39 2022


Interesting study on the difficulty
of favicon.ico request


@author: Robert J McGinness
"""

import socket
from sys import exit
import errno


def kill_favicon(connection: socket.socket, css_handler = None, js_handler = None, image_handler = None) -> None:
    ''' Wait a second for a fetch to be sent from the browser.
        If it comes, process and wait again.  If you get favicon, 404 it!
        
        ######NEEDS TO BE TESTED FOR MUTLIPLE FETCHES, EX favicon, then css,
        etc.
    '''
    
    while True:
        
        try:
            connection.settimeout(1) ###this actually serves to determine if the connection has closed
            request = connection.recv(2048).decode()
            connection.settimeout(None)
            if '/favicon' in request:
                favicon_killer = 'HTTP/1.1 404\nConnection: keep-alive\n\r\n'
                
                favicon_killer = bytes(favicon_killer.encode('utf-8'))
                
                # connection.sendall(favicon_killer)
                
                data_sent = 0
                while data_sent < len(favicon_killer):
                    data_sent += connection.send(favicon_killer)
                    print('kill favicon')
                continue
            
            if 'Content-Type: text/css' in request:
                css_handler(request) # just try, if it fails, or is none raises exception
                print('Do something to send css')
                continue
            
            if 'Content-Type: text/javascript' in request:
                js_handler(request) # just try, if it fails, or is none raises exception
                print('Do something to send javascript')
                continue
                
            if 'Content-Type: image/' in request:
                image_handler(request) # just try, if it fails, or is none raises exception
                print('Do something to send image')
                continue
           
                
        except socket.timeout:
            
            break
        except OSError as e:
            ######BAD FILE DESCRIPTOR (NEED TO CHANGE THIS TO USE ERRNO MODULE)
            ######THIS IS RAISED WHEN THE TIMEOUT IS CHANGED ON A CLOSED SOCKET
            if e.errno == 9:
                break
            raise
        finally:
            connection.close() # just to be sure

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
        
        The final thing to test, in favicon_kill_tester.py,is what is
        being fetched by the browser, ie. favicon.ico, css, js, image,
        whatever.  It uses a loop after every request resetting a time
        out for a next request each iteration. It will test each time
        for favicon.  If not found, it will check if css or script or
        image in Contect-Type HTTP header. In the server, the original
        request will be routed to be properly handled.
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
                
            #####TEST FOR SWITCHING AROUND TIMEOUTS TO SUGGEST IF MULTIPLE
            #####FETCH REQUESTS CAN BE HANDLED THIS WAY
            ##############################################################
            ######TEST RESULT: WORKS FINE
            try:
                connection.settimeout(1)
                connection.settimeout(None)
                connection.settimeout(1)
            except OSError as e:
                print("DIDNT LIKE CHANGING AROUND THE TIMEOUT", e)
                raise
            
            
            kill_favicon(connection) # no handlers passed here
            # count = 1
            # while True:
                
            #     try:
            #         print('Set Time Out', count)
            #         count += 1
            #         connection.settimeout(1) ###this actually serves to determine if the connection has closed
            #         request = connection.recv(2048).decode()
            #         connection.settimeout(None)
            #         if '/favicon' in request:
            #             favicon_killer = 'HTTP/1.1 404\nConnection: keep-alive\n\r\n'
                        
            #             favicon_killer = bytes(favicon_killer.encode('utf-8'))
                        
            #             # connection.sendall(favicon_killer)
                        
            #             data_sent = 0
            #             while data_sent < len(favicon_killer):
            #                 data_sent += connection.send(favicon_killer)
            #                 print('kill favicon')
            #             continue
                    
            #         if 'Content-Type: text/css' in request:
            #             print('Do something to send css')
            #             continue
                    
            #         if 'Content-Type: text/javascript' in request:
            #             print('Do something to send javascript')
            #             continue
                        
            #         if 'Content-Type: image/' in request:
            #             print('Do something to send image')
            #             continue
                   
                        
            #     except socket.timeout:
                    
            #         break
            #     except OSError as e:
            #         print(e, e.errno)
            #         if e.errno == 9:
            #             print('Errno 9')
            #             break
            #         raise
            #     finally:
            #         "In finally"
            #         connection.close()
                    
            
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
            