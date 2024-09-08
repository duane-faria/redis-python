import socket
from typing import Protocol, Optional

class IRedisServer(Protocol):
    host: str
    port: int
    server_socket: socket.socket
    master: Optional[dict[str, str]]
    is_replica: bool
    server_type: str
    master_socket_connection: Optional[socket.socket]
    def replicate(self, data: any) -> None:
        """Method to handle replication logic for the Redis server."""
        pass