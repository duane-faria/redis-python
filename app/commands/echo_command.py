from app.abstract.command import Command
from app.resp_handlers import RESPEncoder


class EchoCommand(Command):
    def execute(self):
        self.send(RESPEncoder.encode(self.payload[0]))
