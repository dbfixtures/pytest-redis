"""Redis async client fixture factory."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from types import ModuleType
from typing import Literal, TypeGuard

import pytest
from redis.asyncio import Redis

from pytest_redis.config import get_config
from pytest_redis.executor import NoopRedis, RedisExecutor

try:
    import pytest_asyncio
except ImportError:  # pragma: no cover
    pytest_asyncio = None  # type: ignore[assignment]


def installed(module: ModuleType | None) -> TypeGuard[ModuleType]:
    """Return True if pytest-asyncio is installed."""
    return module is not None


def _unavailable_stub() -> Callable[[pytest.FixtureRequest], AsyncIterator[Redis]]:
    """Return a sync fixture raising a helpful error when pytest-asyncio is missing."""

    @pytest.fixture
    def redisdb_async_stub(request: pytest.FixtureRequest) -> AsyncIterator[Redis]:
        """Raise ImportError, as async fixtures are unavailable in this environment."""
        raise ImportError(
            "pytest-asyncio is required for async fixtures. "
            "Install it with: pip install 'pytest-redis[async]'"
        )

    return redisdb_async_stub


def redisdb_async(
    process_fixture_name: str, dbnum: int = 0, *, decode: bool | None = None
) -> Callable[[pytest.FixtureRequest], AsyncIterator[Redis]]:
    """Create async connection fixture factory for pytest-redis.

    .. warning::

        Requires ``pytest-asyncio``.

    :param process_fixture_name: name of the process fixture
    :param dbnum: number of database to use
    :param decode: Client: to decode response or not.
        See redis.StrictRedis decode_response client parameter.
    :returns: function which makes an async connection to redis
    """
    if not installed(pytest_asyncio):
        return _unavailable_stub()

    @pytest_asyncio.fixture
    async def redisdb_async_factory(request: pytest.FixtureRequest) -> AsyncIterator[Redis]:
        """Create async connection for pytest-redis.

        #. Load required process fixture.
        #. Get redis module and config.
        #. Connect to redis.
        #. Flush database after tests.
        #. Close the client, releasing its connection pool.

        :param request: fixture request object
        :returns: Redis async client
        """
        proc_fixture: NoopRedis | RedisExecutor = request.getfixturevalue(process_fixture_name)
        config = get_config(request)

        redis_host = proc_fixture.host
        redis_port = proc_fixture.port
        redis_username = proc_fixture.username
        redis_password = proc_fixture.password
        redis_db = dbnum
        decode_responses: Literal[True] | Literal[False] = (
            decode if decode is not None else config.decode
        )

        redis_client = Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            username=redis_username,
            password=redis_password,
            unix_socket_path=proc_fixture.unixsocket,
            decode_responses=decode_responses,
        )

        try:
            yield redis_client
        finally:
            try:
                await redis_client.flushall()
            finally:
                await redis_client.aclose()

    return redisdb_async_factory
