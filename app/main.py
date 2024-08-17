# Uncomment this to pass the first stage
import socket
import threading
from enum import Enum

# constants
ARRAY_IDENTIFIER: str = '*'
SIMPLE_STRING_IDENTIFIER: str = '+'
BULK_STRING_IDENTIFIER: str = '$'

class Params(Enum):
    PX = 'px' # expiry in milliseconds

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
    def encode(value: str | None) -> bytes:

        if isinstance(value, str) and len(value) <= 4:
            return f"{SIMPLE_STRING_IDENTIFIER}{value}\r\n".encode("utf-8")

        if isinstance(value, str):
            return f"{BULK_STRING_IDENTIFIER}{len(value)}\r\n{value}\r\n".encode("utf-8")

        if value is None:
            return f"{BULK_STRING_IDENTIFIER}-1\r\n".encode("utf-8")

        return b''

class Store:
  data = {}

  @staticmethod
  def set_value(key, value):
    Store.data[key] = value

  @staticmethod
  def get_value(key):
    return Store.data[key]

  @staticmethod
  def delete_value(key):
    del Store.data[key]

class ExecuteFunctionAfterXMilliSeconds:
    @staticmethod
    def execute(milliseconds: int, function):
        delay_in_seconds = milliseconds / 1000

        timer = threading.Timer(delay_in_seconds, function)

        timer.start()
        print('started timer', milliseconds)

class RedisServer:
    def __init__(self, host: str, port: int):
        self.server_socket = socket.create_server((host, port))

    def start(self ):
        while True:
            conn, _ = self.server_socket.accept()
            threading.Thread(target=self._handle_client, args=(conn,)).start()

    def _get_payload_params(self, payload: list[str]):
        params = {}

        if Params.PX.value in payload:
           index = payload.index(Params.PX.value)
           value = payload[index + 1]
           params[Params.PX.value] = value

        return params

    def _apply_params(self, params: [Params, str], command: str, payload: list[str]):
        if Params.PX.value in params:
            if command == 'set':
                key_value = payload[0]

                remove_item = lambda: Store.delete_value(key_value)

                ExecuteFunctionAfterXMilliSeconds.execute(milliseconds=int(params[Params.PX.value]), function=remove_item)

    def _get_response(self, command: str, payload: [str, None] = None) -> str:
        response = ''

        if command == 'ping':
            response = "PONG"

        if command == 'echo':
            response = payload[0]

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
            response = "role:master"

        return response

    def _parse_payload(self, payload: list):
        return [item[1] for item in payload]

    def _handle_client(self, conn: socket.socket):
        with conn:
            while True:
                encoded_message = conn.recv(1024)

                command_and_payload = RESPParser(encoded_message.decode('utf-8')).parse()

                command = list(command_and_payload[0])[1].lower()
                payload = self._parse_payload(command_and_payload[1:]) or None
                print('command', command)
                print('payload', payload)
                response = self._get_response(command, payload)

                conn.send(RESPEncoder.encode(response))


class HandleCliParams:
    @staticmethod
    def execute() -> int | None:
        import argparse
        parser = argparse.ArgumentParser(description='Get CLI params')

        # Add arguments
        parser.add_argument('--port', type=int, help='Server port')

        # Parse the arguments
        args = parser.parse_args()

        return args.port or None

def main():
    port = HandleCliParams().execute() or 6379
    RedisServer(host='localhost', port=port).start()

if __name__ == "__main__":
    main()
