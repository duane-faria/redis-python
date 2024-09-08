from app.abstract.command import Command
from app.config import replicas
from app.resp_handlers import RESPEncoder
from app.utils import GenerateRandomString


class PsyncCommand(Command):
    def execute(self):
        replication_id = GenerateRandomString(length=40).execute()
        response = [RESPEncoder.simple_string_encode(f"FULLRESYNC {replication_id} 0")]

        rdb_hex = "524544495330303131fa0972656469732d76657205372e322e30fa0a72656469732d62697473c040fa056374696d65c26d08bc65fa08757365642d6d656dc2b0c41000fa08616f662d62617365c000fff06e3bfec0ff5aa2"
        rdb_content = bytes.fromhex(rdb_hex)
        rdb_length = f"${len(rdb_content)}\r\n".encode()
        response.append(rdb_length + rdb_content)
        replicas.append(self.connection)

        for res in response:
            self.send(res)