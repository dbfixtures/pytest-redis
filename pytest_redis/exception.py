"""Pytest-Redis exceptions."""


class RedisUnsupported(Exception):
    """Exception raised when an unsupported Redis version is detected."""


class RedisMisconfigured(Exception):
    """Exception raised when the redis_exec points to non existing file."""


class UnixSocketTooLong(Exception):
    """Exception raised when unixsocket path is too long."""
