from enum import Enum

class CommandEnum(Enum):
    PING = 'ping'
    ECHO = 'echo'
    GET = 'get'
    SET = 'set'
    INFO = 'info'
    REPLCONF = 'replconf'
    PSYNC = 'psync'