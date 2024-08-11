# Uncomment this to pass the first stage
import socket
import threading

PONG = "+PONG\r\n"


def wait_for_messages(conn, address):
    # wait for client
    print(address)
    with conn:
        while True:
            command = conn.recv(1024)
            conn.send(PONG.encode())


def main():
    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        conn, address = server_socket.accept()
        threading.Thread(target=wait_for_messages, args=(conn, address)).start()


if __name__ == "__main__":
    main()
