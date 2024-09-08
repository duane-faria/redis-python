from app.abstract.command import Command
from app.resp_handlers import RESPEncoder
from app.store import Store


class GetCommand(Command):
    def execute(self):
        key = self.payload[0]
        print('store values: ', Store.get_values())
        try:
            response = Store.get_value(key)
        except KeyError:
            response = None

        self.send(RESPEncoder.encode(response))