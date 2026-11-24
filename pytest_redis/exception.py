"""Pytest-Redis exceptions."""

from packaging.version import Version


class RedisUnsupported(Exception):
    """Exception raised when an unsupported Redis version is detected."""

    _MESSAGE = (
        "Your version of Redis is not supported. "
        "Consider updating to Redis {min_version} at least. "
        "The currently installed version of Redis: {current_version}."
    )

    @classmethod
    def unsupported_version(
        cls, min_version: Version, current_version: Version
    ) -> "RedisUnsupported":
        """Create an exception for an unsupported Redis version."""
        return cls(cls._MESSAGE.format(min_version=min_version, current_version=current_version))


class RedisMisconfigured(Exception):
    """Exception raised when the redis_exec points to non existing file."""

    @classmethod
    def invalid_executable(cls, executable: str) -> "RedisMisconfigured":
        """Create an exception when the redis executable cannot be run."""
        return cls(f"Bad path to redis_exec is given: {executable} not exists or wrong program")

    @classmethod
    def unparseable_option(cls, option: str, error: ValueError) -> "RedisMisconfigured":
        """Create an exception when a redis option line cannot be parsed."""
        return cls(f"Can't parse option {option!r}: {error}")

    @classmethod
    def invalid_option_name(cls, name: str, option: str) -> "RedisMisconfigured":
        """Create an exception when an option name is not a valid redis-server option."""
        return cls(f"{name!r} isn't a redis-server option name: {option!r}")

    @classmethod
    def managed_option(cls, name: str, option: str) -> "RedisMisconfigured":
        """Create an exception when a managed option is passed in options."""
        return cls(
            f"pytest-redis sets {name!r} itself, so it can't be passed in options: {option!r}"
        )

    @classmethod
    def include_option_disallowed(cls, option: str) -> "RedisMisconfigured":
        """Create an exception when the include option is passed in options."""
        return cls(
            f"'include' loads a file that can change what pytest-redis sets, "
            f"so it can't be passed in options: {option!r}"
        )

    @classmethod
    def duplicate_setting_option(cls, name: str, setting: str, option: str) -> "RedisMisconfigured":
        """Create an exception when an option should use a dedicated setting instead."""
        return cls(f"Set {name!r} with the {setting!r} setting, not in options: {option!r}")

    @classmethod
    def option_value_starts_with_dash(cls, option: str) -> "RedisMisconfigured":
        """Create an exception when an option value starts with '--'."""
        return cls(f"A value starting with '--' could be read as another option: {option!r}")


class UnixSocketTooLong(Exception):
    """Exception raised when unixsocket path is too long."""

    @classmethod
    def path_too_long(cls, max_length: int, unixsocket: str) -> "UnixSocketTooLong":
        """Create an exception when the unixsocket path exceeds the system limit."""
        return cls(
            f"Unix Socket path is longer than {max_length} "
            f"allowed on your system: {unixsocket}. "
            f"It's probably due to the temporary directory configuration. "
            f"You can configure that for python by changing TMPDIR envvar, "
            f"add for example `--basetemp=/tmp/pytest` to your pytest "
            f"command or add `addopts = --basetemp=/tmp/pytest` to your "
            f"pytest configuration file."
        )
