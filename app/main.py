import binascii
import socket
import threading
import sys
import gzip

class Headers:
    def __init__(self, content_type="text/plain", content_length=None, content_encoding=None, accept_encoding=None):
        self.content_type = content_type
        self.content_length = content_length
        self.content_encoding = content_encoding
        self.accept_encoding = accept_encoding
    
    def encode(self):
        pass

class Request:
    def __init__(self, request):
        self.raw_request = request
        self._headers = {}
        self._body = ""
        self._request_line = ""
        self._method = ""
        self._path = ""
    
    def parse_request_header(self):
        pass

    def parse_request_body(self):
        pass

    def parse_request_line(self):
        pass 

    @property
    def headers(self):
        pass 

    @property
    def body(self):
        pass 

    @property
    def request_line(self):
        pass

    @property
    def method(self):
        pass
    
    @property
    def path(self):
        pass

    def __str__(self):
        return self.raw_request
    
class Response:
    def __init__(self,http_version="HTTP/1.1" , status=200, headers=Headers(), body=""):
        self.status = status
        self.headers = headers
        self.body = body
        self.messages = {
            200: "OK",
            201: "Created",
            404: "Not Found"
        }

    def encode(self):
        pass





def main():
    def read_header(request, key):
        request = request.lower()
        if key in request:
            return request.split(f"{key}: ")[1].split("\r\n")[0]
        return ""
    
    def extract_request_line(request):
        request_line = request.split("\r\n")[0]
        method, path, _ = request_line.split(" ")
        return method, path

    def get_request_body(request):
        return request.split("\r\n")[-1]

    def destructure_path(path):
        path = path[1:]
        return path.split("/")
    
    def handle_connection(conn: socket.socket , addr):
        with conn:
            request = conn.recv(1024)
            data = request.decode()
            method, path = extract_request_line(data)
            
            path = destructure_path(path)
            if not path[0]:
                msg = "HTTP/1.1 200 OK\r\n\r\n"
            elif path[0] == "echo":
                echo_string = path[-1]
                client_compression = [compression.strip() for compression in read_header(data, "accept-encoding").split(",")]
                content_encoding = ""

                if "gzip" in client_compression:
                    content_encoding = f"content-encoding: gzip\r\n"
                    echo_string = gzip.compress(echo_string.encode())
                    print(echo_string)
                    conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_string)}\r\n{content_encoding}\r\n".encode() + echo_string)
                    return

                msg = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_string)}\r\n{content_encoding}\r\n{echo_string}" 
            elif path[0] == "user-agent":
                user_agent = read_header(data, "user-agent")
                msg = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}"
            elif path[0] == "files":
                args = sys.argv
                files_path = args[-1]
                if method == "GET":
                    try:
                        with open(files_path + "/" + path[-1], "r") as file:
                            file_content = file.read()
                            msg = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(file_content)}\r\n\r\n{file_content}"
                    except FileNotFoundError:
                        msg = "HTTP/1.1 404 Not Found\r\n\r\n"
                elif method == "POST":
                    request_body = get_request_body(data)
                    with open(files_path + "/" + path[-1], "w") as file:
                        file.write(request_body)
                    msg = "HTTP/1.1 201 Created\r\n\r\n"
                else:
                    msg = "HTTP/1.1 404 Not Found\r\n\r\n"
            else:
                msg = "HTTP/1.1 404 Not Found\r\n\r\n"
            conn.sendall(msg.encode())

    with socket.create_server(("localhost", 4221)) as socket_server:
        print("Server started at port 4221")
        while True: 
            conn, addr = socket_server.accept()
            threading.Thread(target=handle_connection, args=(conn, addr)).start()



if __name__ == "__main__":
    main()
