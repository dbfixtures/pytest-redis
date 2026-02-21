"""Redis client fixture factory."""

from typing import Callable, Generator, Literal

import pytest
import redis
from _pytest.fixtures import FixtureRequest

from pytest_redis.config import get_config
from pytest_redis.executor import NoopRedis, RedisExecutor


def redisdb(
    process_fixture_name: str, dbnum: int = 0, decode: bool | None = None
) -> Callable[[FixtureRequest], Generator[redis.Redis, None, None]]:
    """Create connection fixture factory for pytest-redis.

    :param process_fixture_name: name of the process fixture
    :param dbnum: number of database to use
    :param decode: Client: to decode response or not.
        See redis.StrictRedis decode_response client parameter.
    :returns: function which makes a connection to redis
    """

    @pytest.fixture
    def redisdb_factory(request: FixtureRequest) -> Generator[redis.Redis, None, None]:
        """Create connection for pytest-redis.

        #. Load required process fixture.
        #. Get redis module and config.
        #. Connect to redis.
        #. Flush database after tests.

        :param FixtureRequest request: fixture request object
        :rtype: redis.client.Redis
        :returns: Redis client
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

        redis_client = redis.Redis(
            redis_host,
            redis_port,
            redis_db,
            username=redis_username,
            password=redis_password,
            unix_socket_path=proc_fixture.unixsocket,
            decode_responses=decode_responses,
        )

        yield redis_client
        redis_client.flushall()

    return redisdb_factory
