"""Redis async client fixture factory."""

from typing import Callable, Generator, Literal, Optional, Union

import pytest
import redis.asyncio import Redis
from _pytest.fixtures import FixtureRequest

from pytest_redis.config import get_config
from pytest_redis.executor import NoopRedis, RedisExecutor


def async_redisdb(
    process_fixture_name: str, dbnum: int = 0, decode: Optional[bool] = None
) -> Callable[[FixtureRequest], Generator[redis.Redis, None, None]]:
    """Create connection fixture factory for pytest-redis.

    :param process_fixture_name: name of the process fixture
    :param dbnum: number of database to use
    :param decode: Client: to decode response or not.
        See redis.StrictRedis decode_reponse client parameter.
    :returns: function which makes a connection to redis
    """

    @pytest.fixture
    async def async_redisdb_factory(request: FixtureRequest) -> Generator[redis.Redis, None, None]:
        """Create connection for pytest-redis.

        #. Load required process fixture.
        #. Get redis module and config.
        #. Connect to redis.
        #. Flush database after tests.

        :param FixtureRequest request: fixture request object
        :rtype: redis.client.Redis
        :returns: Redis client
        """
        proc_fixture: Union[NoopRedis, RedisExecutor] = request.getfixturevalue(
            process_fixture_name
        )
        config = get_config(request)

        redis_host = proc_fixture.host
        redis_port = proc_fixture.port
        redis_username = proc_fixture.username
        redis_password = proc_fixture.password
        redis_db = dbnum
        decode_responses: Union[Literal[True], Literal[False]] = (
            decode if decode is not None else config["decode"]
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
        await redis_client.flushall()

    return async_redisdb_factory
