from app.entities import CommandConfig
from abc import ABC, abstractmethod

from app.enums import ParamsEnum, CommandEnum

class Command(ABC):
    def __init__(self, command_config: CommandConfig) -> None:
        self.payload = command_config.payload
        self.connection = command_config.socket_connection
        self.params = {}
        self.redis_server = command_config.server_instance

    @abstractmethod
    def execute(self) -> None:
        pass

    def apply_params(self):
        pass

    def _find_param_value(self, param):
        index = self.payload.index(param)
        value = self.payload[index + 1]
        return value

    def get_params(self):
        params = [
            ParamsEnum.PX.value,
            ParamsEnum.LISTENING_PORT.value,

        ]

        for param in params:
            if param in self.payload:
                self.params[param] = self._find_param_value(param)

        return self.params

    def send(self, data: bytes):
        self.connection.sendall(data)