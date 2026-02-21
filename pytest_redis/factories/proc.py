"""Redis process fixture factory."""

from pathlib import Path
from typing import Callable, Generator, Iterable

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.tmpdir import TempPathFactory
from port_for import PortForException, PortType, get_port

from pytest_redis.config import RedisConfig, get_config
from pytest_redis.executor import RedisExecutor


def _redis_port(port: PortType | None, config: RedisConfig, excluded_ports: Iterable[int]) -> int:
    """User specified port, otherwise find an unused port from config."""
    redis_port = get_port(port, excluded_ports) or get_port(config.port, excluded_ports)
    if redis_port is None:
        raise PortForException(
            "Could not determine a Redis port from the provided port spec or config."
        )
    return redis_port


def redis_proc(
    executable: str | None = None,
    timeout: int | None = None,
    host: str | None = None,
    port: PortType = -1,
    username: str | None = None,
    password: str | None = None,
    db_count: int | None = None,
    save: str | None = None,
    compression: bool | None = None,
    checksum: bool | None = None,
    syslog: bool | None = None,
    loglevel: str | None = None,
    datadir: str | None = None,
    modules: list[str] | None = None,
) -> Callable[[FixtureRequest, TempPathFactory], Generator[RedisExecutor, None, None]]:
    """Fixture factory for pytest-redis.

    :param executable: path to redis-server
    :param timeout: client's connection timeout
    :param host: hostname
    :param port:
        exact port (e.g. '8000', 8000)
        randomly selected port (None) - any random available port
        [(2000,3000)] or (2000,3000) - random available port from a given range
        [{4002,4003}] or {4002,4003} - random of 4002 or 4003 ports
        [(2000,3000), {4002,4003}] -random of given orange and set
    :param username: username
    :param password: password
    :param db_count: number of databases redis should have
    :param save: redis save configuration setting
    :param compression: Compress redis dump files
    :param checksum: Whether to add checksum to the rdb files
    :param syslog:Whether to enable logging to the system logger
    :param loglevel: redis log verbosity level.
        One of debug, verbose, notice or warning
    :param datadir: Path for redis data files, including the unix domain socket.
        If this is not configured, then a temporary directory is created and used
        instead.
    :param modules: list of paths of Redis extension modules to load
    :returns: function which makes a redis process
    """

    @pytest.fixture(scope="session")
    def redis_proc_fixture(
        request: FixtureRequest, tmp_path_factory: TempPathFactory
    ) -> Generator[RedisExecutor, None, None]:
        """Fixture for pytest-redis.

        #. Get configs.
        #. Run redis process.
        #. Stop redis process after tests.

        :param request: fixture request object
        :param tmpdir_factory:
        :rtype: pytest_redis.executors.TCPExecutor
        :returns: tcp executor
        """
        config = get_config(request)
        redis_exec = executable or config.exec
        rdbcompression: bool = config.compression if compression is None else compression
        rdbchecksum: bool = config.rdbchecksum if checksum is None else checksum
        syslog_enabled: bool = config.syslog if syslog is None else syslog

        port_path = tmp_path_factory.getbasetemp()
        if hasattr(request.config, "workerinput"):
            port_path = tmp_path_factory.getbasetemp().parent

        n = 0
        used_ports: set[int] = set()
        while True:
            try:
                redis_port = _redis_port(port, config, used_ports)
                port_filename_path = port_path / f"redis-{redis_port}.port"
                if redis_port in used_ports:
                    raise PortForException(
                        f"Port {redis_port} already in use, "
                        f"probably by other instances of the test. "
                        f"{port_filename_path} is already used."
                    )
                used_ports.add(redis_port)
                with port_filename_path.open("x") as port_file:
                    port_file.write(f"redis_port {redis_port}\n")
                break
            except FileExistsError:
                n += 1
                if n >= config.port_search_count:
                    raise PortForException(
                        f"Attempted {n} times to select ports. "
                        f"All attempted ports: {', '.join(map(str, used_ports))} are already "
                        f"in use, probably by other instances of the test."
                    ) from None

        if datadir:
            redis_datadir = Path(datadir)
        elif config.datadir:
            redis_datadir = Path(config.datadir)
        else:
            redis_datadir = tmp_path_factory.mktemp(f"pytest-redis-{request.fixturename}")

        redis_modules = modules or config.modules

        redis_executor = RedisExecutor(
            executable=redis_exec,
            databases=db_count or config.db_count,
            redis_timeout=timeout or config.timeout,
            loglevel=loglevel or config.loglevel,
            rdbcompression=rdbcompression,
            rdbchecksum=rdbchecksum,
            syslog_enabled=syslog_enabled,
            save=save or config.save,
            host=host or config.host,
            port=redis_port,
            username=username or config.username,
            password=password or config.password,
            startup_timeout=60,
            datadir=redis_datadir,
            modules=redis_modules,
        )
        with redis_executor:
            yield redis_executor

    return redis_proc_fixture
