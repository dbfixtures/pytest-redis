"""Redis executor."""

import os
import platform
import re
import shlex
from itertools import islice
from pathlib import Path
from tempfile import gettempdir
from typing import Any, Literal

from mirakuru import TCPExecutor
from packaging.version import Version, parse

from pytest_redis.exception import RedisMisconfigured, RedisUnsupported, UnixSocketTooLong

MAX_UNIXSOCKET = 104
if platform.system() == "Linux":
    MAX_UNIXSOCKET = 107


def extract_version(text: str) -> Version:
    """Extract version number from the text.

    :param text: text that contains the version number
    """
    matches = re.search(r"\d+(?:\.\d+)+", text)
    assert matches is not None
    return parse(matches.group(0))


class RedisExecutor(TCPExecutor):
    """Redis executor.

    Extended TCPExecutor to contain all required logic for parametrizing
    and properly constructing command to start redis-server.
    """

    MIN_SUPPORTED_VERSION: Version = parse("2.6")
    """
    Minimum required version of redis that is accepted by pytest-redis.
    """

    MANAGED_OPTIONS: frozenset[str] = frozenset(
        {
            "daemonize",
            "rdbcompression",
            "rdbchecksum",
            "appendonly",
            "databases",
            "timeout",
            "pidfile",
            "unixsocket",
            "dbfilename",
            "logfile",
            "loglevel",
            "syslog-enabled",
            "bind",
            "port",
            "dir",
        }
    )
    """
    Options pytest-redis always sets itself, which can't be passed as extra options.
    """

    OPTION_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
    """
    What an option name passed in options may look like.
    """

    def __init__(
        self,
        executable: str,
        databases: int,
        redis_timeout: int,
        loglevel: str,
        host: str,
        port: int,
        username: str | None = None,
        password: str | None = None,
        startup_timeout: int = 60,
        save: str = "",
        daemonize: str = "no",
        *,
        rdbcompression: bool = True,
        rdbchecksum: bool = False,
        syslog_enabled: bool = False,
        appendonly: str = "no",
        datadir: Path | None = None,
        modules: list[str] | None = None,
        options: list[str] | None = None,
    ) -> None:  # pylint:disable=too-many-locals
        """Init method of a RedisExecutor.

        :param executable: path to redis-server
        :param databases: number of databases
        :param redis_timeout: client's connection timeout
        :param loglevel: redis log verbosity level
        :param host: server's host
        :param port: server's port
        :param username: server's username
        :param password: server's password
        :param startup_timeout: executor's timeout for start and stop actions
        :param log_prefix: prefix for log filename
        :param save: redis save configuration setting
        :param daemonize:
        :param rdbcompression: Compress redis dump files
        :param rdbchecksum: Whether to add checksum to the rdb files
        :param syslog_enabled: Whether to enable logging
            to the system logger
        :param datadir: location where all the process files will be located
        :param appendonly:
        :param modules: list of paths of Redis extension modules to load
        :param options: extra redis-server options, each in redis.conf line
            syntax (``name value``)
        """
        if not datadir:
            datadir = Path(gettempdir())
        self.unixsocket = str(datadir / f"redis.{port}.sock")
        self.executable = executable

        self.username = username
        self.password = password

        logfile_path = datadir / f"redis-server.{port}.log"
        pidfile_path = datadir / f"redis-server.{port}.pid"

        command = [
            self.executable,
            "--daemonize",
            daemonize,
            "--rdbcompression",
            self._redis_bool(rdbcompression),
            "--rdbchecksum",
            self._redis_bool(rdbchecksum),
            "--appendonly",
            appendonly,
            "--databases",
            str(databases),
            "--timeout",
            str(redis_timeout),
            "--pidfile",
            str(pidfile_path),
            "--unixsocket",
            self.unixsocket,
            "--dbfilename",
            f"dump.{port}.rdb",
            "--logfile",
            str(logfile_path),
            "--loglevel",
            loglevel,
            "--syslog-enabled",
            self._redis_bool(syslog_enabled),
            "--bind",
            str(host),
            "--port",
            str(port),
            "--dir",
            str(datadir),
        ]
        if password:
            command.extend(["--requirepass", str(password)])
        if save:
            if self.version < parse("7"):
                save_parts = save.split()
                assert all(part.isdigit() for part in save_parts), (
                    "all save arguments should be numbers"
                )
                assert len(save_parts) % 2 == 0, (
                    "there should be even number of elements passed to save"
                )
                for time, change in zip(
                    islice(save_parts, 0, None, 2), islice(save_parts, 1, None, 2)
                ):
                    command.extend([f"--save {time} {change}"])
            else:
                command.extend([f"--save {save}"])

        if modules:
            for module_path in modules:
                command.extend(["--loadmodule", module_path])

        if options:
            # requirepass is always refused, so the client fixtures know the password
            set_by_setting = {"requirepass": "password"}
            if save:
                set_by_setting["save"] = "save"
            if modules:
                set_by_setting["loadmodule"] = "modules"
            command.extend(self._extra_options(options, set_by_setting))

        super().__init__(command, host, port, timeout=startup_timeout)

    @classmethod
    def _extra_options(
        cls, options: list[str], set_by_setting: dict[str, str] | None = None
    ) -> list[str]:
        """Turn redis.conf style lines into redis-server arguments.

        :param options: entries such as ``"maxmemory 100mb"``
        :param set_by_setting: options that come from a pytest-redis setting
            in this run, mapped to that setting's name
        :returns: arguments such as ``["--maxmemory", "100mb"]``
        :raises RedisMisconfigured: if an entry can't be parsed, has a name that
            isn't a plain option name, sets an option pytest-redis sets itself,
            or has a value redis-server could read as another option
        """
        set_by_setting = set_by_setting or {}
        arguments = []
        for option in options:
            try:
                parts = shlex.split(option)
            except ValueError as exc:
                raise RedisMisconfigured(f"Can't parse option {option!r}: {exc}") from exc
            if not parts:
                continue
            name, *values = parts
            if not cls.OPTION_NAME.fullmatch(name):
                # redis-server doesn't quote option names, so "'port 6390'" would set port
                raise RedisMisconfigured(f"{name!r} isn't a redis-server option name: {option!r}")
            if name.lower() in cls.MANAGED_OPTIONS:
                raise RedisMisconfigured(
                    f"pytest-redis sets {name!r} itself, "
                    f"so it can't be passed in options: {option!r}"
                )
            if setting := set_by_setting.get(name.lower()):
                raise RedisMisconfigured(
                    f"Set {name!r} with the {setting!r} setting, not in options: {option!r}"
                )
            if any(value.startswith("--") for value in values):
                # redis-server can read an argument starting with -- as a new option,
                # which could set port
                raise RedisMisconfigured(
                    f"A value starting with '--' could be read as another option: {option!r}"
                )
            arguments.extend([f"--{name}", *values])
        return arguments

    @classmethod
    def _redis_bool(cls, value: Any) -> Literal["yes", "no"]:
        """Convert the boolean value to redis's yes/no.

        :param bool value: boolean value to convert
        :returns: yes for True, no for False
        :rtype: str
        """
        return "yes" if value and value != "no" else "no"

    def start(self) -> "RedisExecutor":
        """Check supported version before starting."""
        self._check_unixsocket_length()
        self._check_version()
        super().start()
        return self

    def _check_unixsocket_length(self) -> None:
        """Check unixsocket length."""
        if len(self.unixsocket) > MAX_UNIXSOCKET:
            raise UnixSocketTooLong(
                f"Unix Socket path is longer than {MAX_UNIXSOCKET} "
                f"allowed on your system: {self.unixsocket}. "
                f"It's probably due to the temporary directory configuration. "
                f"You can configure that for python by changing TMPDIR envvar, "
                f"add for example `--basetemp=/tmp/pytest` to your pytest "
                f"command or add `addopts = --basetemp=/tmp/pytest` to your "
                f"pytest configuration file."
            )

    @property
    def version(self) -> Any:
        """Return redis version."""
        with os.popen(f"{self.executable} --version") as version_output:
            version_string = version_output.read()
        if not version_string:
            raise RedisMisconfigured(
                f"Bad path to redis_exec is given: {self.executable} not exists or wrong program"
            )

        return extract_version(version_string)

    def _check_version(self) -> None:
        """Check redises version if it's compatible."""
        redis_version = self.version
        if redis_version < self.MIN_SUPPORTED_VERSION:
            raise RedisUnsupported(
                f"Your version of Redis is not supported. "
                f"Consider updating to Redis {self.MIN_SUPPORTED_VERSION} at least. "
                f"The currently installed version of Redis: {redis_version}."
            )
