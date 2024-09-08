from app.abstract.command import Command
from app.enums import ParamsEnum
from app.resp_handlers import RESPEncoder


class ReplConfCommand(Command):
    def execute(self):
        params = self.get_params()

        if ParamsEnum.GETACK in params:
            offset = 0
            return self.send(RESPEncoder.array_encode(['REPLCONF', 'ACK', offset]))

        self.send(RESPEncoder.encode('OK'))