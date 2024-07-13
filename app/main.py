import socket


def main():
    def read_header(request, key):
        headers = request.split("\r\n")[1:]
        for header in headers:
            if key == header[:len(key)].lower():
                return header.split(": ")[1]
        return None
    
    def extract_request_line(request):
        request_line = request.split("\r\n")[0]
        method, path, _ = request_line.split(" ")
        return method, path

    def destructure_path(path):
        path = path[1:]
        return path.split("/")
    
    with socket.create_server(("localhost", 4221)) as socket_server:
        print("Server started at port 4221")
        while True: 
            conn, addr = socket_server.accept()
            with conn:
                request = conn.recv(1024)
                data = request.decode()
                method, path = extract_request_line(data)
                
                path = destructure_path(path)

                if not path[0]:
                    msg = "HTTP/1.1 200 OK\r\n\r\n"
                elif path[0] == "echo":
                    echo_string = path[-1] 
                    msg = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_string)}\r\n\r\n{echo_string}" 
                elif path[0] == "user-agent":
                    user_agent = read_header(data, "user-agent")
                    msg = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}"
                else:
                    msg = "HTTP/1.1 404 Not Found\r\n\r\n"
                conn.sendall(msg.encode())


if __name__ == "__main__":
    main()
