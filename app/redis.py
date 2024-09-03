import socket
import threading
from enum import Enum

from app.resp_handlers import RESPEncoder, RESPParser
from app.commands import CommandFactory, load_commands
from app.config import replicas

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
            print(dir(self.master_socket_connection))
            print(self.master_socket_connection.getsockname())
            self.send_hand_shake()

        print('')
    
    def start(self):
        while True:
            conn, client_address = self.server_socket.accept()
            threading.Thread(target=self._handle_client, args=(conn,client_address)).start()

    def replicate(self, data: any):
        print('replicating...')
        for repl in replicas:
            repl.sendall(data)

    def send_hand_shake(self):
        # sends messages to the master to configure the replica

        def await_response():
            self.master_socket_connection.recv(1024)

        self.master_socket_connection.sendall(RESPEncoder.array_encode('PING'))
        await_response()
        self.master_socket_connection.sendall(RESPEncoder.array_encode(['REPLCONF', 'listening-port', str(self.port)]))
        await_response()
        self.master_socket_connection.sendall(RESPEncoder.array_encode(['REPLCONF', 'capa', 'psync2']))
        await_response()
        self.master_socket_connection.sendall(RESPEncoder.array_encode(['PSYNC', '?', '-1']))

    def _handle_client(self, client_socket: socket.socket, client_address):
        with client_socket:
            while True:
                encoded_message = client_socket.recv(1024)
                if encoded_message == b'':
                    return

                command_and_payload = RESPParser(encoded_message.decode('utf-8')).parse()
                command_name = command_and_payload[0].lower()
                payload = command_and_payload[1:] if len(command_and_payload) > 1 else None
                print('command', command_name)
                print('payload', payload)

                command_factory = CommandFactory()
                load_commands(command_factory)
                this = self
         
                command = command_factory.get_command(command_name=command_name, payload=payload,
                                                      connection=client_socket, redis_server=this)
                command.execute()
                print('command acabou de ser executado, é replica:', self.is_replica)
                if not self.is_replica and command_name in ['set', 'del']:
                    print('caiu no if do master replica')
                    payload_to_replicate = RESPEncoder.array_encode(command_and_payload)
                    self.replicate(payload_to_replicate)
  

# python3 -m pdb app.main --port 6379
# printf '+PING\r\n' | nc localhost 6379
# printf '*2\r\n$4\r\necho\r\n$5\r\nduane\r\n' | nc localhost 6379
#printf *3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n | nc localhost 6379