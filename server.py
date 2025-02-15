#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        #receive the requests from client
        self.status = 200  #self.status is used to check the status code and control the status_200 function

        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\r\n" % self.data)
        print(self.data.decode("utf-8"))

        request_type = self.get_request_method(self.data.decode('utf-8'))
        file_location = self.get_file_location(self.data.decode('utf-8'))
        file_content = self.check_file_content(file_location)

        print(request_type)
        print("\r\n")
        print(file_location)

        self.status_405(request_type)
        self.status_404(file_location)
        self.status_301(file_location)
        self.status_200(file_location, file_content)
    

    def get_request_method(self, data):
        """
        Find what type of Request we are getting
        """
        #return the string of request_type
        return str(data).split(' ')[0]

    def get_file_location(self, data):
        """
        This function returns the location the requested file lies
        """

        file_location = './www' + str(data).split(' ')[1]

        if file_location[-1] == '/':
            file_location += 'index.html'

        return file_location

    def check_file_content(self, file_location):
        """
        This function returns the type of current file
        """
        
        file_types = ['html', 'css']
        for type in file_types:
            if type in file_location:
                return 'Content-Type:text/' + type
        return 'Content-Type:text/plain'
    
    # 200: OK
    def status_200(self, file_location, file_content):
        if self.status == 200:
            self.request.sendall(bytearray("HTTP/1.1 200 OK\r\n",'utf-8'))
            self.request.sendall(bytearray(file_content + '\r\n' + '\r\n\r\n', 'utf-8'))
            self.request.sendall(bytearray(open(file_location, 'r').read() + '\r\n', 'utf-8'))
            return
    
    # 301: Moved Permently
    def status_301(self, URL):
        """
        This function checks URLs to see if there is a match
        """
        
        if "./www/deep" == URL:
            print("redirected to: " + URL + " :Sending 301 status code\r\n")
            self.request.sendall(bytearray('HTTP/1.1 301 Moved Permanently\r\n','utf-8'))
            self.request.sendall(bytearray('Correct location: /deep/\r\n', 'utf-8'))
            self.status = 301
            return

    # 404: Not Found
    def status_404(self, URL):
        """
        This function checks if a 404 error 
        (if the path does not exist )
        """

        if not os.path.exists(URL):
            print("Non-exis path: " + URL + ":Send 404 status code\r\n")
            self.request.sendall(bytearray('HTTP/1.1 404 Not Found\r\n', 'utf-8'))
            self.status = 404
            return
        
        if '../' in URL:
            print("Non-exist path: " + URL + ":Send 404 status code\r\n")
            self.request.sendall(bytearray('HTTP/1.1 404 Not Found\r\n', 'utf-8'))
            self.status = 404
            return
        

    # 405: Method Not Allowed
    def status_405(self, type):
        """
        VALID HANDLE: GET
        INVALID HANDLE: POST/PUT/DELETE return "405 Method Not Allowed"
        """
        if not type == 'GET':
            print("Invalid request: " + type + ":Sending 405 status code\r\n")
            self.request.sendall(bytearray('HTTP/1.1 405 Method Not Allowed\r\n', 'utf-8'))
            self.status = 405
            return
        


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
