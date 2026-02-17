"""Reddis class respsenting an instance started by a third party."""

import socket

from mirakuru import TCPExecutor


class NoopRedis(TCPExecutor):
    """Reddis class respsenting an instance started by a third party."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str | None = None,
        password: str | None = None,
        unixsocket: str | None = None,
        startup_timeout: int = 15,
    ) -> None:
        """Init method of NoopRedis.

        :param host: server's host
        :param port: server's port
        :param username: server's username
        :param password: server's password
        :param timeout: executor's timeout for start and stop actions
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        # TODO: Can this be actually, arbitrary None?
        self.unixsocket = unixsocket
        self.timeout = startup_timeout
        super().__init__([], host, port, timeout=startup_timeout)

    def start(self) -> "NoopRedis":
        """Start is a NOOP."""
        self._set_timeout()
        self.wait_for(self.redis_available)
        return self

    def redis_available(self) -> bool:
        """Return True if connecting to Redis is possible."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(0.1)
                s.connect((self.host, self.port))
            except (TimeoutError, ConnectionRefusedError):
                return False
        return True
