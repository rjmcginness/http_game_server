# -*- coding: utf-8 -*-
"""
Created on Wed May  4 08:14:39 2022

@author: rmcginness
"""

import socketserver
import socket

class Test:
    def __init__(self, sock):
        self.sock = sock
    
    def write(self, data):
        print(data)
        
class Server(socket.socket):
    def __init__(self, address: str, port: int) -> None:
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((address, port))
        print('Bound:', address, port)
    
    def start(self) -> None:
        self.listen(4)
        
        with self as sock:
            # sock.bind(('localhost', 5550))
            # sock.listen(1)
            
            connection, address = sock.accept()
            with connection:
                request = connection.recv(1024)
                print("REQUEST:", request)
                output = output_bytes()
                connection.sendall(output)
                request = connection.recv(1024)
                print("REQUEST:", request)
                if '.css' in request.decode().split()[1]:
                    connection.sendall(read_css('menu.css'))
                #input('press enter')
            
            #######BELOW FOR MULTIPLE CONNECTIONS: need to spawn threads 
            
            # while True:
            #     connection, address = sock.accept()
            #     with connection:
            #         request = connection.recv(1024)
            #         print("REQUEST:", request)
            #         output = output_bytes()
            #         connection.sendall(output)
            #         connection.sendall(read_css('menu.css'))
            #         input('press enter')

def read_css(file_name: str):
    css_text = bytes('HTTP/1.1 200 OK\nContent-Type: text/css; charset=utf-8\n\r\n'.encode('utf-8'))
    with open(file_name, 'rb') as css_file:
        css_text += css_file.read().strip()
    
    return css_text

def output_bytes():
    output = "HTTP/1.1 200 OK\n"
    output += "Content-Type: text/html; charset=utf-8\n"
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <title>Test</title>
    <link rel="stylesheet"" type="text/css" href="menu.css"/>
</head>
<body>
    <a href="/war">War</a>
    <form action="/War" method="get">
        <input type="submit" value="War"/>
    </form>
</body>
</html>\n'''#"<!DOCTYPE html><html><body>Hello, World!</body></html>\n"
    ######NEEDED THIS TO END IN \n\r\n
    output += f"Content-Length: {len(html)}\n\r\n" + html 
    return bytes(output.encode('utf-8'))

class GameTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        t = Test(self.socket)
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        #print(self.data)
        t.write(self.data)
        # just send back the same data, but upper-cased
        #self.request.sendall(self.data.upper())
        output = '''HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8\n\r\n<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <title>Test</title>
</head>
<body>
    <a href="/war">War</a>
    <form action="/War" method="get">
        <input type="submit" value="War"/>
    </form>
</body>
</html>\r\n'''
        self.request.send(bytes(output.strip()), 'utf-8')
        
if __name__ == '__main__':
    print("Starting server...")
    server = Server('localhost', 7700)
    server.start()
    
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    #     sock.bind(('localhost', 5550))
    #     sock.listen(1)
    #     connection, address = sock.accept()
    #     with connection:
    #         request = connection.recv(1024)
    #         output = output_bytes()
    #         total_sent = 0
    #         connection.sendall(output)#bytes("<!DOCTYPE html><html><body>Hello, World!</body></html>\n".encode('utf-8')))
            # while total_sent < len(output):
            #     print(output)
                #total_sent += connection.send(output)
            
            # request = connection.recv(1024)
            #print(request.decode())
            # input("Press enter")
    
    # with socketserver.TCPServer(('localhost', 6550), GameTCPHandler) as server:
    #     server.serve_forever()
    
    # portlist = [21, 22, 23, 80]
    # for port in portlist:
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    #         result = sock.connect_ex(('localhost',port))
    #         print(port, ":", result)
    
        
    
    
        