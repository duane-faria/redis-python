import socket

from app.command import CommandProcessor
from app.entities import CommandConfig
from app.resp_handlers import RESPParser

def is_utf8_encoded(data: bytes) -> bool:
    try:
        data.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False

class SocketMessage:
    def __init__(self, socket_connection: socket.socket, server_instance, is_master = False):
        self.socket_connection = socket_connection
        self.server_instance = server_instance
        self.command_config: CommandConfig | None = None
        self.is_master = is_master

    def _run_command(self, command_and_payload: list):
        print('_run_command')
        print(command_and_payload, 'command_and_payload')
        command_name = command_and_payload[0].lower()
        payload = command_and_payload[1:] if len(command_and_payload) > 1 else None

       # if len(command_name) == 0 or command_name == '':
            #return

        self.command_config = CommandConfig(
            name=command_name,
            payload=payload,
            socket_connection=self.socket_connection,
            server_instance=self.server_instance,
            is_master=self.is_master
        )
        print('command', command_name)
        print('payload', payload)

        command_processor = CommandProcessor(
            command_config=self.command_config
        )
        command_processor.execute()

    def execute(self, encoded_message: bytes) -> None:
        if encoded_message == b'' or not is_utf8_encoded(encoded_message):
            return

        decoded_message = RESPParser(encoded_message).parse()
        print(decoded_message, 'decoded_message')
        if isinstance(decoded_message, list) and isinstance(decoded_message[0], list):
            for message in decoded_message:
                self._run_command(message)
        else:
            self._run_command(decoded_message)