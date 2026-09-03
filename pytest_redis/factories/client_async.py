"""Redis async client fixture factory."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from types import ModuleType
from typing import Literal, TypeGuard, cast

import pytest
from _pytest.fixtures import FixtureRequest
from redis.asyncio import Redis

from pytest_redis.config import get_config
from pytest_redis.executor import NoopRedis, RedisExecutor

try:
    import pytest_asyncio
except ImportError:  # pragma: no cover
    pytest_asyncio = None  # type: ignore[assignment]


def installed(module: ModuleType | None) -> TypeGuard[ModuleType]:
    """Return True if pytest-asyncio is installed.

    Takes the module as an argument, rather than reading the global directly,
    so that the ``None`` case stays visible to type checkers while
    ``pytest_asyncio`` itself keeps the module type that the
    ``@pytest_asyncio.fixture`` decorator needs.
    """
    return module is not None


def _unavailable_stub() -> Callable[[FixtureRequest], AsyncIterator[Redis]]:
    """Return a sync fixture raising a helpful error when pytest-asyncio is missing."""

    @pytest.fixture
    def redisdb_async_stub(request: FixtureRequest) -> None:
        """Raise ImportError, as async fixtures are unavailable in this environment."""
        raise ImportError(
            "pytest-asyncio is required for async fixtures. "
            "Install it with: pip install pytest-redis[async]"
        )

    return cast("Callable[[FixtureRequest], AsyncIterator[Redis]]", redisdb_async_stub)


def redisdb_async(
    process_fixture_name: str, dbnum: int = 0, decode: bool | None = None
) -> Callable[[FixtureRequest], AsyncIterator[Redis]]:
    """Create async connection fixture factory for pytest-redis.

    Requires ``pytest-asyncio``, installable with
    ``pip install pytest-redis[async]``.

    :param process_fixture_name: name of the process fixture
    :param dbnum: number of database to use
    :param decode: Client: to decode response or not.
        See redis.StrictRedis decode_response client parameter.
    :returns: function which makes an async connection to redis
    """
    if not installed(pytest_asyncio):
        return _unavailable_stub()

    @pytest_asyncio.fixture
    async def redisdb_async_factory(request: FixtureRequest) -> AsyncIterator[Redis]:
        """Create async connection for pytest-redis.

        #. Load required process fixture.
        #. Get redis module and config.
        #. Connect to redis.
        #. Flush database after tests.
        #. Close the client, releasing its connection pool.

        :param FixtureRequest request: fixture request object
        :rtype: redis.asyncio.client.Redis
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

        # Unlike the sync client, redis.asyncio.Redis takes keyword arguments only.
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
            await redis_client.flushall()
        finally:
            await redis_client.aclose()

    return cast("Callable[[FixtureRequest], AsyncIterator[Redis]]", redisdb_async_factory)
