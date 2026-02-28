"""Redis noop fixture factory."""

from typing import Callable, Generator

import pytest
from _pytest.fixtures import FixtureRequest

from pytest_redis.config import get_config
from pytest_redis.executor import NoopRedis


def redis_noproc(
    host: str | None = None,
    port: int | None = None,
    username: str | None = None,
    password: str | None = None,
    startup_timeout: int = 15,
) -> Callable[[FixtureRequest], Generator[NoopRedis, None, None]]:
    """Nooproc fixture factory for pytest-redis.

    :param host: hostname
    :param port: exact port (e.g. '8000', 8000)
    :param username: username used for authentication
    :param password: password used for authentication
    :param startup_timeout: Blocking wait until we give up connecting to Redis.
    :returns: function which makes a redis process
    """

    @pytest.fixture(scope="session")
    def redis_noproc_fixture(request: FixtureRequest) -> Generator[NoopRedis, None, None]:
        """Nooproc fixture for pytest-redis.

        Builds mock executor to run tests with

        :param FixtureRequest request: fixture request object
        :rtype: pytest_redis.executors.TCPExecutor
        :returns: tcp executor
        """
        config = get_config(request)
        redis_noopexecutor = NoopRedis(
            host=host or config.host,
            port=port or config.port or 6379,
            username=username or config.username,
            password=password or config.password,
            unixsocket=None,
            startup_timeout=startup_timeout,
        )

        with redis_noopexecutor:
            yield redis_noopexecutor

    return redis_noproc_fixture
