from app.abstract.command import Command
from app.enums import ParamsEnum
from app.resp_handlers import RESPEncoder
from app.store import Store
from app.utils import ExecuteFunctionAfterXMilliSeconds


class SetCommand(Command):
    def execute(self):
        key = self.payload[0]
        value = self.payload[1]
        Store.set_value(key, value)
        params = self.get_params()

        if len(params) > 0:
            self.apply_params()

        self.send(RESPEncoder.encode('OK'))

    def apply_params(self):
        key_value = self.payload[0]
        remove_item = lambda: Store.delete_value(key_value)
        # @TODO pass this class as a param, to make it easier to test
        ExecuteFunctionAfterXMilliSeconds.execute(milliseconds=int(self.params[ParamsEnum.PX.value]),
                                                  function=remove_item)