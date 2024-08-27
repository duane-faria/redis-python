import socket
import threading
from enum import Enum

from app.resp_handlers import RESPEncoder, RESPParser
from app.utils import GenerateRandomString, ExecuteFunctionAfterXMilliSeconds
from app.store import Store
from app.commands import CommandFactory, load_commands

class Params(Enum):
    PX = 'px' # expiry in milliseconds
    
class CommandEnum(Enum): 
    PING = 'ping'          

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
    
    def start(self):
        while True:
            conn, _ = self.server_socket.accept()
            threading.Thread(target=self._handle_client, args=(conn,)).start()

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


    def _handle_master_socket_messages(self, connection):
        with connection:
            while True:
                encoded_message = connection.recv(1024)

                RESPParser(encoded_message.decode('utf-8')).parse()

    def master_socket_listener(self):
        #while True:
        connection, _ = self.master_socket_connection.accept()
        threading.Thread(target=self._handle_master_socket_messages, args=(connection,)).start()



    def _get_payload_params(self, payload: list[str]):
        params = {}

        if Params.PX.value in payload:
           index = payload.index(Params.PX.value)
           value = payload[index + 1]
           params[Params.PX.value] = value

        return params

    def _apply_params(self, params: Params, command: str, payload: list[str]):
        if Params.PX.value in params:
            if command == 'set':
                key_value = payload[0]

                remove_item = lambda: Store.delete_value(key_value)

                ExecuteFunctionAfterXMilliSeconds.execute(milliseconds=int(params[Params.PX.value]), function=remove_item)

    def handle_command(self, command: str, payload: list[str] | None = None, connection: socket.socket = None) -> None:
        response: None | bytes | str | list = ''

        if command == 'ping':
            connection.send(RESPEncoder.encode('PONG'))

        if command == 'echo':
             connection.send(RESPEncoder.encode(payload[0]))

        if command == 'set':
            key = payload[0]
            value = payload[1]
            Store.set_value(key, value)
            params = self._get_payload_params(payload)

            if len(params) > 0:
                self._apply_params(params=params, payload=payload, command=command)

            response = 'OK'

        if command == 'get':
            key = payload[0]
            try:
                response = Store.get_value(key)
            except KeyError:
                response = None

        if command == 'info':
            _type = 'slave' if self.master is not None else 'master'
            replication_id = GenerateRandomString(length=40).execute()
            role_type = f"role:{_type}"

            string_list = [role_type, f"master_replid:{replication_id}", "master_repl_offset:0"]

            if _type == 'master':
                response = RESPEncoder.bulk_string_encode("\r\n".join(string_list))
            else: # means it's a replica
                response = RESPEncoder.bulk_string_encode(role_type)

        if command == 'replconf':
            response = "OK"

        if command == 'psync':
            replication_id = GenerateRandomString(length=40).execute()
            response = [RESPEncoder.simple_string_encode(f"FULLRESYNC {replication_id} 0")]

            rdb_hex = "524544495330303131fa0972656469732d76657205372e322e30fa0a72656469732d62697473c040fa056374696d65c26d08bc65fa08757365642d6d656dc2b0c41000fa08616f662d62617365c000fff06e3bfec0ff5aa2"
            rdb_content = bytes.fromhex(rdb_hex)
            rdb_length = f"${len(rdb_content)}\r\n".encode()
            response.append(rdb_length + rdb_content)

        return response

    def _handle_client(self, conn: socket.socket):
        with conn:
            while True:
                encoded_message = conn.recv(1024)
                command_and_payload = RESPParser(encoded_message.decode('utf-8')).parse()
                
                command_name = command_and_payload[0].lower()
                payload = command_and_payload[1:] if len(command_and_payload[1]) > 0 else None
                print('command', command_name)
                print('payload', payload)

                command_factory = CommandFactory()
                load_commands(command_factory)
                this = self
         
                command = command_factory.get_command(command_name=command_name,  payload=payload, connection=conn, redis_server=this)
                command.execute()      
  

# python3 -m app.main --port 6379 
# printf '+PING\r\n' | nc localhost 6379
# printf '*2\r\n$4\r\necho\r\n$5\r\nduane\r\n' | nc localhost 6379