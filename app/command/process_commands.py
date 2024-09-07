from app.commands import CommandFactory, load_commands
from app.entities import CommandConfig

class CommandProcessor:
    def __init__(self, command_config: CommandConfig):
        self.command_config = command_config
        self.command_factory = self.load_command_factory()

    def load_command_factory(self):
        command_factory = CommandFactory()
        load_commands(command_factory)
        return command_factory

    def execute(self):
        command = self.command_factory.get_command(command_config=self.command_config)
        return command.execute()

