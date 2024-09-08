from app.abstract.command import Command
from app.commands import EchoCommand, GetCommand, SetCommand, InfoCommand, ReplConfCommand, PsyncCommand, PingCommand
from app.entities import CommandConfig
from app.enums import CommandEnum


class CommandFactory:
    def __init__(self) -> None:
        self.commands: dict[str, type[Command]] = {}

    def register_command(self, command_name: str, command_class: type[Command]):
        self.commands[command_name] = command_class

    def get_command(self, command_config: CommandConfig):
        command_class = self.commands.get(command_config.name)

        return command_class(command_config=command_config)


def load_commands(command_factory: CommandFactory) -> CommandFactory:
    """Register commands with the given commands factory and returns it."""
    command_factory.register_command(CommandEnum.PING.value, PingCommand)
    command_factory.register_command(CommandEnum.ECHO.value, EchoCommand)
    command_factory.register_command(CommandEnum.GET.value, GetCommand)
    command_factory.register_command(CommandEnum.SET.value, SetCommand)
    command_factory.register_command(CommandEnum.INFO.value, InfoCommand)
    command_factory.register_command(CommandEnum.REPLCONF.value, ReplConfCommand)
    command_factory.register_command(CommandEnum.PSYNC.value, PsyncCommand)

    return command_factory