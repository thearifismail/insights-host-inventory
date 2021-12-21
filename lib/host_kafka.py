import socket
from contextlib import closing

from app.config import Config
from app.environment import RuntimeEnvironment
from app.logging import get_logger

logger = get_logger(__name__)


def _any_bootstrap_server_connects(kafka_socket, servers) -> bool:
    if not servers:
        config = Config(RuntimeEnvironment.SERVICE)
        servers = [config.bootstrap_servers] if isinstance(config.bootstrap_servers, str) else config.bootstrap_servers

    try:
        for server in servers:
            try:
                host, port = server.split(":")
                new_addr = (host, int(port))

                # connect_ex() returns zero when the socket is open and accessible
                errcode = kafka_socket.connect_ex(new_addr)
                if not errcode:
                    return True

            except ValueError as ve:
                logger.error(f"Invalid server address: {str(ve)}")
    except ValueError as ve:
        logger.error(f"No servers available: {str(ve)}")


def kafka_available(servers=None):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as kafka_socket:
        return _any_bootstrap_server_connects(kafka_socket, servers)
