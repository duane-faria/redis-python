class CommandConfig:
    def __init__(self, name, payload, socket_connection, server_instance, is_master = False):
        self.name = name
        self.payload = payload
        self.socket_connection = socket_connection
        self.server_instance = server_instance
        self.is_master = is_master