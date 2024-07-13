import socket


def main():
    def extract_request_line(request):
        request_line = request.split("\r\n")[0]
        method, path, _ = request_line.split(" ")
        return method, path
    
    with socket.create_server(("localhost", 4221)) as socket_server:
        print("Server started at port 4221")
        while True: 
            conn, addr = socket_server.accept()
            with conn:
                request = conn.recv(1024)
                data = request.decode()
                method, path = extract_request_line(data)

                if path == "/":
                    msg = f"HTTP/1.1 200 OK\r\n\r\n"
                else:
                    msg = f"HTTP/1.1 404 Not Found\r\n\r\n"
                
                conn.sendall(msg.encode())


                

if __name__ == "__main__":
    main()
