"""Redis async client fixture factory."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from types import ModuleType
from typing import TYPE_CHECKING, Literal, TypeGuard, cast

import pytest
from _pytest.fixtures import FixtureRequest
from packaging.version import parse

from pytest_redis.config import get_config
from pytest_redis.executor import NoopRedis, RedisExecutor

# The first pytest-asyncio 1.x, matching the pytest >= 8.4 floor of pytest-redis
# itself. Older releases do provide ``pytest_asyncio.fixture``, but are not
# supported here.
MIN_PYTEST_ASYNCIO_VERSION = parse("1.0.0")

if TYPE_CHECKING:
    from redis.asyncio import Redis
else:
    try:
        # redis.asyncio has been introduced in redis 4.2.0
        from redis.asyncio import Redis
    except ImportError:  # pragma: no cover
        Redis = None

try:
    import pytest_asyncio
except ImportError:  # pragma: no cover
    pytest_asyncio = None  # type: ignore[assignment]


def supports_async_fixtures(module: ModuleType | None) -> TypeGuard[ModuleType]:
    """Return True if pytest-asyncio is installed at a version providing async fixtures."""
    if module is None:
        return False
    return parse(module.__version__) >= MIN_PYTEST_ASYNCIO_VERSION


def async_support_available() -> bool:
    """Return True if both pytest-asyncio and an async capable redis are importable."""
    return supports_async_fixtures(pytest_asyncio) and Redis is not None


def _missing_requirements() -> list[str]:
    """Return the requirements of the async fixtures unmet in this environment."""
    missing = []
    if not supports_async_fixtures(pytest_asyncio):
        missing.append("pytest-asyncio >= 1.0.0")
    if Redis is None:
        missing.append("redis >= 4.2.0")
    return missing


def _unavailable_stub() -> Callable[[FixtureRequest], AsyncIterator[Redis]]:
    """Return a sync fixture raising a helpful error when async support is missing."""
    missing = " and ".join(_missing_requirements())

    @pytest.fixture
    def redisdb_async_stub(request: FixtureRequest) -> None:
        """Raise ImportError, as async fixtures are unavailable in this environment."""
        raise ImportError(
            f"{missing} required for async fixtures. Install with: pip install pytest-redis[async]"
        )

    return cast("Callable[[FixtureRequest], AsyncIterator[Redis]]", redisdb_async_stub)


def redisdb_async(
    process_fixture_name: str, dbnum: int = 0, decode: bool | None = None
) -> Callable[[FixtureRequest], AsyncIterator[Redis]]:
    """Create async connection fixture factory for pytest-redis.

    Requires ``pytest-asyncio`` >= 1.0.0 and ``redis`` >= 4.2.0,
    installable with ``pip install pytest-redis[async]``.

    :param process_fixture_name: name of the process fixture
    :param dbnum: number of database to use
    :param decode: Client: to decode response or not.
        See redis.StrictRedis decode_response client parameter.
    :returns: function which makes an async connection to redis
    """
    if not async_support_available():
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
