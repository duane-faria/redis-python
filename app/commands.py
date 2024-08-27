import socket
from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol, Optional

from app.resp_handlers import RESPEncoder
from app.store import Store
from app.utils import GenerateRandomString, ExecuteFunctionAfterXMilliSeconds

class IRedisServer(Protocol):
    host: str
    port: int
    server_socket: socket.socket
    master: Optional[dict[str, str]]
    is_replica: bool
    server_type: str
    master_socket_connection: Optional[socket.socket]

class Params(Enum):
    PX = 'px' # expiry in milliseconds

class Command(ABC):
    def __init__(self, payload: list[str] | None, connection: socket.socket = None, redis_server: IRedisServer = None) -> None:
        self.payload = payload
        self.connection = connection
        self.params = {}
        self.redis_server = redis_server
    
    @abstractmethod
    def execute(self):
        pass
    
    def get_params(self):
        if Params.PX.value in self.payload:
            index = self.payload.index(Params.PX.value)
            value = self.payload[index + 1]
            self.params[Params.PX.value] = value

        return self.params
    
    def apply_params(self):
        pass
        

class PingCommand(Command):
    def execute(self):
        self.connection.send(RESPEncoder.encode('PONG'))
        
        
class EchoCommand(Command):
    def execute(self):
       self.connection.send(RESPEncoder.encode(self.payload[0]))
       

class SetCommand(Command):
    def execute(self):
        key = self.payload[0]
        value = self.payload[1]
        Store.set_value(key, value)
        params = self.get_params()

        if len(params) > 0:
            self.apply_params()

        self.connection.send(RESPEncoder.encode('OK'))
    
    def apply_params(self):
        key_value = self.payload[0]
        remove_item = lambda: Store.delete_value(key_value)
        # @TODO pass this class as a param, to make it easier to test
        ExecuteFunctionAfterXMilliSeconds.execute(milliseconds=int(self.params[Params.PX.value]), function=remove_item)
        

class GetCommand(Command):
    def execute(self):
        key = self.payload[0]
        try:
            response = Store.get_value(key)
        except KeyError:
            response = None
        
        self.connection.send(RESPEncoder.encode(response))
        
        
class InfoCommand(Command):
    def execute(self):
        replication_id = GenerateRandomString(length=40).execute()
        role_type = f"role:{self.redis_server.server_type}"

        string_list = [role_type, f"master_replid:{replication_id}", "master_repl_offset:0"]

        if not self.redis_server.is_replica:
            response = RESPEncoder.bulk_string_encode("\r\n".join(string_list))
        else: # means it's a replica
            response = RESPEncoder.bulk_string_encode(role_type)
        
        self.connection.send(response)
        
        
class ReplConfCommand(Command):
    def execute(self):
        self.connection.send(RESPEncoder.encode('OK'))
        

class PsyncCommand(Command):
    def execute(self):
        replication_id = GenerateRandomString(length=40).execute()
        response = [RESPEncoder.simple_string_encode(f"FULLRESYNC {replication_id} 0")]

        rdb_hex = "524544495330303131fa0972656469732d76657205372e322e30fa0a72656469732d6269"
        +"7473c040fa056374696d65c26d08bc65fa08757365642d6d656dc2b0c41000fa08616f662d62617365c000fff06e3bfec0ff5aa2"
        rdb_content = bytes.fromhex(rdb_hex)
        rdb_length = f"${len(rdb_content)}\r\n".encode()
        response.append(rdb_length + rdb_content)
        self.connection.send(response)
        
        
class CommandFactory():
    def __init__(self) -> None:
        self.commands: dict[str, type[Command]] = {}
    
    def register_command(self, command_name: str, command_class: Command):
        self.commands[command_name] = command_class
    
    def get_command(self, command_name: str, *args, **kwargs):
        command_class = self.commands.get(command_name)
        print(command_name)
        return command_class(*args, **kwargs)
    
    
def load_commands(command_factory: CommandFactory) -> CommandFactory:
    """Registers commands with the given command factory and returns it."""
    command_factory.register_command('ping', PingCommand)
    command_factory.register_command('echo', EchoCommand)
    command_factory.register_command('set', SetCommand)
    command_factory.register_command('get', GetCommand)
    
    return command_factory
        
        