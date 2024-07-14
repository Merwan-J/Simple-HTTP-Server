import binascii
import re
import socket
import threading
import sys
import gzip
from typing import List

class Headers:
    def __init__(self, content_type=None, content_length=None, content_encoding=None, accept_encoding=None, user_agent=None):
        self.content_type = content_type
        self.content_length = content_length
        self.content_encoding = content_encoding
        self.accept_encoding = accept_encoding
        self.user_agent = user_agent

    @classmethod
    def from_request(cls, headers_list: List[str]):
        headers = {key: value for key, value in (header.split(': ') for header in headers_list if header)}
        content_type = headers.get("Content-Type", None)
        content_length = headers.get("Content-Length", None)
        content_encoding = headers.get("Content-Encoding", None)
        accept_encoding = headers.get("Accept-Encoding", None)
        user_agent = headers.get("User-Agent", None)

        return cls(content_type, content_length, content_encoding, accept_encoding, user_agent)

    def encode(self):
        headers_list = [
            *([f"Content-Type: {self.content_type}"] if self.content_type is not None else []),
            *([f"Content-Length: {self.content_length}"] if self.content_length is not None else []),
            *([f"Content-Encoding: {self.content_encoding}"] if self.content_encoding is not None else []),
            *([f"Accept-Encoding: {self.accept_encoding}"] if self.accept_encoding is not None else []),
            *([f"User-Agent: {self.user_agent}"] if self.user_agent is not None else [])
        ]

        headers_str = "\r\n".join(headers_list) + "\r\n\r\n"
        return headers_str.encode('utf-8')

class Request:
    def __init__(self, request):
        self.raw_request = request
        self.header = None
        self.body = ""
        self.method = ""
        self.path = ""
        self.parse_request()
    
    def parse_request(self):
        pattern = r'^(POST|GET|PUT|DELETE|OPTIONS|HEAD) (\/\S*) HTTP\/1\.1\r\n((?:[^\r\n]+\r\n)*)(?:\r\n)?([\s\S]*)'
        match = re.match(pattern, self.raw_request)
        method, path, headers, body = match.groups()

        self.method = method
        self.path = path
        self.header = Headers.from_request(headers.split("\r\n"))
        self.body = body

    def __str__(self):
        return self.raw_request
    
class Response:
    def __init__(self, status=200, headers=Headers(), body=""):
        self.status = status
        self.headers = headers
        self.body = body
        self.messages = {
            200: "OK",
            201: "Created",
            404: "Not Found"
        }

    def encode(self):
        response_line = f"HTTP/1.1 {self.status} {self.messages.get(self.status, 'Unknown')}\r\n".encode()
        headers = self.headers.encode()
        body = self.body.encode() if type(self.body) == str else self.body
        return response_line + headers + body
        
def read_file(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        return None

def write_to_file(file_path, data):
    with open(file_path, "w") as file:
        file.write(data)

def main():
    def handle_connection(conn: socket.socket , addr):
        with conn:
            raw_request = conn.recv(1024)
            request = Request(raw_request.decode())
            path, headers = request.path.split("/")[1:], request.header
            response = Response()
            
            if not path[0]:
                response.status = 200
            elif path[0] == "echo":
                echo_string = path[-1]
                client_compression = request.header.accept_encoding or ""

                if "gzip" in [compression.strip() for compression in client_compression.split(",")]:
                    echo_string = gzip.compress(echo_string.encode())
                    response.headers.content_encoding = "gzip"  
                
                response.headers.content_type = "text/plain"
                response.headers.content_length = len(echo_string)              
                response.body = echo_string

            elif path[0] == "user-agent":
                user_agent = headers.user_agent
                response.headers.content_type = "text/plain"
                response.headers.content_length = len(user_agent)
                response.body = user_agent

            elif path[0] == "files":
                args = sys.argv
                files_path = args[-1]
                if request.method == "GET":
                    file_content = read_file(files_path + "/" + path[-1])
                    if file_content:
                        response.headers.content_type = "application/octet-stream"
                        response.headers.content_length = len(file_content)
                        response.body = file_content
                    else:
                        response.status = 404
                elif request.method == "POST":
                    write_to_file(files_path + "/" + path[-1], request.body)
                    response.status = 201
                else:
                    response.status = 404
            else:
                response.status = 404
            conn.sendall(response.encode())

    with socket.create_server(("localhost", 4221)) as socket_server:
        print("Server started at port 4221")
        while True: 
            conn, addr = socket_server.accept()
            threading.Thread(target=handle_connection, args=(conn, addr)).start()



if __name__ == "__main__":
    main()
