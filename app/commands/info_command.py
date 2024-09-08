from app.abstract.command import Command
from app.resp_handlers import RESPEncoder
from app.utils import GenerateRandomString


class InfoCommand(Command):
    def execute(self):
        replication_id = GenerateRandomString(length=40).execute()
        role_type = f"role:{self.redis_server.server_type}"

        string_list = [role_type, f"master_replid:{replication_id}", "master_repl_offset:0"]

        if not self.redis_server.is_replica:
            response = RESPEncoder.bulk_string_encode("\r\n".join(string_list))
        else:  # means it's a replica
            response = RESPEncoder.bulk_string_encode(role_type)

        self.send(response)