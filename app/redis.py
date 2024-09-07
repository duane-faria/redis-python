import socket
import threading

from app.resp_handlers import RESPEncoder
from app.config import replicas
from app.socket_message_handler import SocketMessage

class RedisServer:
    def __init__(self, host: str, port: int, replica = None):
        self.port = port
        self.host = host
        self.server_socket = socket.create_server((host, port))

        self.master = {
            'host': replica.split()[0],
            'port': replica.split()[1]
        } if replica is not None else None
        self.is_replica = self.master is not None
        self.server_type = 'slave' if self.is_replica else 'master'

        if self.is_replica:
            self.master_socket_connection = socket.create_connection((self.master['host'], self.master['port']))
            self.send_hand_shake()
            #threading.Thread(target=self.listen_to_master, args=(self.master_socket_connection,), daemon=True).start()

        print('redis server started\n', 'is replica: ', self.is_replica)

    def listen_to_master(self, master_connection):
        while True:
            socket_message = SocketMessage(
                socket_connection=self.master_socket_connection,
                server_instance=self,
                is_master=True
            )

            encoded_message = master_connection.recv(1024)
            print('listen_to_master', encoded_message)
            socket_message.execute(encoded_message)

    def start(self):
        while True:
            conn, client_address = self.server_socket.accept()
            threading.Thread(target=self._handle_client, args=(conn,client_address), daemon=True).start()

    def replicate(self, data: any):
        print('replicating...')
        for repl in replicas:
            repl.sendall(data)

    def send_hand_shake(self):
        # sends messages to the master to configure the replica
        print('hand shake')
        def await_response():
            self.master_socket_connection.recv(1024)

        self.master_socket_connection.sendall(RESPEncoder.array_encode('PING'))
        await_response()
        self.master_socket_connection.sendall(RESPEncoder.array_encode(['REPLCONF', 'listening-port', str(self.port)]))
        await_response()
        self.master_socket_connection.sendall(RESPEncoder.array_encode(['REPLCONF', 'capa', 'psync2']))
        await_response()
        self.master_socket_connection.sendall(RESPEncoder.array_encode(['PSYNC', '?', '-1']))
        await_response()
        threading.Thread(target=self.listen_to_master, args=(self.master_socket_connection,), daemon=True).start()

    def _handle_client(self, client_socket: socket.socket, client_address):
        with client_socket:
            while True:
                encoded_message = client_socket.recv(1024)
                socket_message = SocketMessage(
                    socket_connection=self.master_socket_connection,
                    server_instance=self
                )

                socket_message.execute(encoded_message)
                command_name = socket_message.command_config.name
                command_payload = socket_message.command_config.payload
                command_and_payload = [command_name, *command_payload]

                if not self.is_replica and command_name in ['set', 'del']:
                    payload_to_replicate = RESPEncoder.array_encode(command_and_payload)
                    self.replicate(payload_to_replicate)
  

# python3 -m pdb app.main --port 6379
# printf '+PING\r\n' | nc localhost 6379
# printf '*2\r\n$4\r\necho\r\n$5\r\nduane\r\n' | nc localhost 6379
#printf *3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n | nc localhost 6379