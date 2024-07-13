import socket


def main():
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
                
                echo_string = destructure_path(path)[-1] 
                msg = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_string)}\r\n\r\n{echo_string}" 
                conn.sendall(msg.encode())


if __name__ == "__main__":
    main()
