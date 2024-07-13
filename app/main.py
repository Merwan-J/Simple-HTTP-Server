import socket


def main():
    with socket.create_server(("localhost", 4221)) as socket_server:
        while True: # keep the server running
            conn, addr = socket_server.accept()
            with conn:
                data = "HTTP/1.1 200 OK\r\n\r\n".encode()
                conn.sendall(data)
                print("Sent data to client with address: ", addr)
                print("Data sent: ", data.decode())


                

if __name__ == "__main__":
    main()
