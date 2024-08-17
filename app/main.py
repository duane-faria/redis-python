# Uncomment this to pass the first stage
import socket
import threading
from enum import Enum

# constants
ARRAY_IDENTIFIER: str = '*'
SIMPLE_STRING_IDENTIFIER: str = '+'
BULK_STRING_IDENTIFIER: str = '$'

class RESPIdentifier(Enum):
    ARRAY: str = '*'
    SIMPLE_STRING: str = '+'
    BULK_STRING: str = '$'

class RESPParser:
    def __init__(self, data):
        self.data = data
    
    def parse(self):
        data_identifier = self.data[0]

        if data_identifier == ARRAY_IDENTIFIER:
            return self._parse_array()

        if data_identifier == SIMPLE_STRING_IDENTIFIER:
           return self._parse_simple_string()

        return ['', '']

    def _parse_array(self):
        broken_data = self.data.split('\r\n')
        filtered_data = filter(self._filter_values, enumerate(broken_data))
        tuple_list = list(filtered_data)
        return tuple_list

    def _parse_simple_string(self):
        command = self.data.replace("\r\n", "")
        return {command[1:], ''}

    def _filter_values(self, tuple_list: tuple[int, str]) -> bool:
        index, value = tuple_list
        return index > 0 and len(value) > 0 and value[0] != '$'


class RESPEncoder:
    def __init__(self):
        pass

    @staticmethod
    def encode(value: str) -> bytes:
        if isinstance(value, str) and len(value) <= 4:
            return f"{SIMPLE_STRING_IDENTIFIER}{value}\r\n".encode("utf-8")

        if isinstance(value, str):
            return f"{BULK_STRING_IDENTIFIER}{len(value)}\r\n{value}\r\n".encode("utf-8")

        if type(value) is None:
            return f"{BULK_STRING_IDENTIFIER}-1\r\n"

        return b''

class Store:
  data = {}

  @staticmethod
  def set_value(key, value):
    Store.data[key] = value

  @staticmethod
  def get_value(key):
    return Store.data[key]

class RedisServer:
    def __init__(self, host: str, port: int):
        self.server_socket = socket.create_server((host, port), reuse_port=True)

    def start(self ):
        while True:
            conn, _ = self.server_socket.accept()
            threading.Thread(target=self._handle_client, args=(conn,)).start()

    def _get_payload_params(self, payload: list[str]):


    def _get_response(self, command: str, payload: [str, None] = None) -> str:
        response = ''

        if command == 'ping':
            response = "PONG"

        if command == 'echo':
            response = payload[0]
            #response = RESPEncoder.encode(payload)

        if command == 'set':
            key = payload[0]
            value = payload[1]
            Store.set_value(key, value)
            response = 'OK'

        if command == 'get':
            key = payload[0]
            response = Store.get_value(key)

        return response

    def _parse_payload(self, payload: list):
        return [item[1] for item in payload]

    def _handle_client(self, conn: socket.socket):
        with conn:
            while True:
                encoded_message = conn.recv(1024)

                command_and_payload = RESPParser(encoded_message.decode('utf-8')).parse()
                print('command and payload', command_and_payload)
                command = list(command_and_payload[0])[1].lower()
                payload = self._parse_payload(command_and_payload[1:]) or None

                response = self._get_response(command, payload)
                print(response, 'response')
                conn.send(RESPEncoder.encode(response))




def main():
    RedisServer(host='localhost', port=6379).start()

if __name__ == "__main__":
    main()
