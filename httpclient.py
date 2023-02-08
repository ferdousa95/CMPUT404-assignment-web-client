#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
from urllib.parse import urlparse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def parsing_url_components(self, url):
        """
        urlparse("scheme://netloc/path;parameters?query#fragment")

        You receive a url and then you parse it for information and separate
        out the netloc, hostname, port, path and query.
        """
        self.parsed_url = ''
        self.hostname = ''
        self.port = ''
        self.path = ''
        self.query = ''
        self.total_path = ''

        self.parsed_url = urlparse(url)
        self.hostname = self.parsed_url.hostname

        # port
        if self.parsed_url.port:
            self.port = self.parsed_url.port
        else:  # port 80 is default if not mentioned.
            self.port = 80

        # path
        if self.parsed_url.path != '':
            self.path = self.parsed_url.path
        else:  # because netloc ends with / if no path.
            self.path = '/'

        # query
        if self.parsed_url.query != '':
            self.query = "?" + self.parsed_url.query

        self.total_path = self.path + self.query

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        parsed_data = data.split('\r\n\r\n')
        print("THIS IS PARSED DATA: " + parsed_data[0])
        code = parsed_data[0].split('\r\n')  # the first line of http
        # split the first line and second col is code
        code = code[0].split()[1]
        return int(code)

    def get_headers(self, data):
        header = data.split('\r\n\r\n')
        return header[0]

    def get_body(self, data):
        body = data.split('\r\n\r\n')
        return body[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def request_builder(self, command, args):
        """
        #request_to_send = command + " {self.}" HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'
        """
        top_part = f"{command} {self.total_path} HTTP/1.1\r\nHost: {self.hostname}\r\n"
        bottom_part = "Connection: close\r\n\r\n"
        response = None

        if command == 'GET':
            request_to_send = top_part + bottom_part
            print("REQUEST TO SEND: " + request_to_send)
            self.sendall(request_to_send)
            response = self.recvall(self.socket)
            return response

        if command == 'POST':
            addtional_header = "Content-Type: application/x-www-form-urlencoded\r\nContent_Length: " + \
                len(args[1]) + "\r\n"
            request_to_send = top_part + \
                addtional_header + bottom_part + args[1]
            self.sendall(request_to_send)
            response = self.recvall(self.socket)
            return response

        return 405

    def GET(self, url, args=None):
        """
        This function takes in a url and then parse it. Get the hostname, port,
        path, queries etc and bring those components together. After that it 
        opens a socket connection to the server and sets a GET request. Then 
        received the reponse and parse it.

        @param -> url - the address of the resource we are trying to collect. 

        @Return -> none
        """
        # TODO: Parse the url and create the socket connection.
        self.parsing_url_components(url)
        self.connect(self.hostname, self.port)

        # TODO: Send the request and get the response.
        response = self.request_builder('GET', args)
        print("THIS IS THE GET RESPONSE: " + response)
        self.close()

        # TODO: Parse the response.
        # header = self.get_headers(response)
        # body = self.get_body(response)

        # code = 500
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        """
        This function takes in a url and then parse it. Get the hostname, port,
        path, queries etc and bring those components together. After that it 
        opens a socket connection to the server and sets a POST request. Then 
        received the reponse and parse it.

        @param - url - the address of the resource we are trying to collect. 

        Return is none
        """
        self.parsing_url_components(url)
        self.connect(self.hostname, self.port)

        response = self.request_builder('POST', args)
        print("THIS IS THE POST RESPONSE: " + response)
        self.close()

        header = self.get_headers(response)
        body = self.get_body(response)

        # code = 500
        # body = ""
        return HTTPResponse(header, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
