from app.abstract.command import Command
from app.resp_handlers import RESPEncoder


class PingCommand(Command):
    def execute(self):
        self.send(RESPEncoder.encode('PONG'))