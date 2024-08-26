import threading

class GenerateRandomString:
    def __init__(self, length):
        self.length = length

    def execute(self):
        import random
        import string

        characters = string.ascii_letters + string.digits

        return ''.join(random.choice(characters) for _ in range(self.length))


class HandleCliParams:
    @staticmethod
    def execute() -> dict[str, str | int | None]:
        import argparse
        parser = argparse.ArgumentParser(description='Get CLI params')

        # Add arguments
        parser.add_argument('--port', type=int, help='Server port')
        parser.add_argument('--replicaof', type=str, help='Replica flag')

        # Parse the arguments
        args = parser.parse_args()
        print('args: ',args)
        return dict(port=args.port or None, replica=args.replicaof or None)


class ExecuteFunctionAfterXMilliSeconds:
    @staticmethod
    def execute(milliseconds: int, function):
        delay_in_seconds = milliseconds / 1000

        timer = threading.Timer(delay_in_seconds, function)

        timer.start()
        print('started timer', milliseconds)