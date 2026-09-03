"""Module containing all tests for pytest-redis async client fixtures."""

import pytest
from redis import Redis as SyncRedis
from redis.asyncio import Redis

import pytest_redis.factories

pytest_asyncio = pytest.importorskip("pytest_asyncio", minversion="1.0.0")

redis_proc4 = pytest_redis.factories.redis_proc(port=6382)
redis_proc5 = pytest_redis.factories.redis_proc(port=6386, password="secretpassword")

redis_noproc4 = pytest_redis.factories.redis_noproc(port=6382, startup_timeout=1)
redis_noproc5 = pytest_redis.factories.redis_noproc(port=6386, password="secretpassword")

# ``redis_other_proc`` lives in conftest.py, shared with the sync client tests.
redis_otherdb_async = pytest_redis.factories.redisdb_async("redis_other_proc")
redisdb4_async = pytest_redis.factories.redisdb_async("redis_proc4")
redisdb5_async = pytest_redis.factories.redisdb_async("redis_proc5")

redisdb4_noop_async = pytest_redis.factories.redisdb_async("redis_noproc4")
redisdb5_noop_async = pytest_redis.factories.redisdb_async("redis_noproc5")

redisdb_async_decode = pytest_redis.factories.redisdb_async("redis_proc", decode=True)
redisdb_async_dbnum = pytest_redis.factories.redisdb_async("redis_proc", dbnum=4)


@pytest.mark.asyncio
async def test_redis_async(redisdb_async: Redis) -> None:
    """Check that it's actually working on redis database."""
    await redisdb_async.set("test1", "test")
    await redisdb_async.set("test2", "test")

    test1 = await redisdb_async.get("test1")
    assert test1 == b"test"

    test2 = await redisdb_async.get("test2")
    assert test2 == b"test"


@pytest.mark.asyncio
async def test_second_redis_async(redisdb_async: Redis, redis_otherdb_async: Redis) -> None:
    """Check that two redis processes are separate ones."""
    await redisdb_async.set("test1", "test")
    await redisdb_async.set("test2", "test")
    await redis_otherdb_async.set("test1", "test_other")
    await redis_otherdb_async.set("test2", "test_other")

    assert await redisdb_async.get("test1") == b"test"
    assert await redisdb_async.get("test2") == b"test"

    assert await redis_otherdb_async.get("test1") == b"test_other"
    assert await redis_otherdb_async.get("test2") == b"test_other"


@pytest.mark.asyncio
@pytest.mark.xdist_group(name="redis4")
async def test_external_redis_async(redisdb4_async: Redis, redisdb4_noop_async: Redis) -> None:
    """Check that nooproc connects to the same redis."""
    await redisdb4_async.set("test1", "test_other")
    await redisdb4_async.set("test2", "test_other")

    assert await redisdb4_async.get("test1") == b"test_other"
    assert await redisdb4_async.get("test2") == b"test_other"

    assert await redisdb4_noop_async.get("test1") == b"test_other"
    assert await redisdb4_noop_async.get("test2") == b"test_other"


@pytest.mark.asyncio
@pytest.mark.xdist_group(name="redis5")
async def test_external_redis_auth_async(redisdb5_async: Redis, redisdb5_noop_async: Redis) -> None:
    """Check that nooproc connects to the same password protected redis."""
    await redisdb5_async.set("test1", "test_other")
    await redisdb5_async.set("test2", "test_other")

    assert await redisdb5_async.get("test1") == b"test_other"
    assert await redisdb5_async.get("test2") == b"test_other"

    assert await redisdb5_noop_async.get("test1") == b"test_other"
    assert await redisdb5_noop_async.get("test2") == b"test_other"


@pytest.mark.asyncio
async def test_redis_async_decode(redisdb_async_decode: Redis) -> None:
    """Check that the decode factory argument reaches the async client."""
    await redisdb_async_decode.set("test1", "test")

    assert await redisdb_async_decode.get("test1") == "test"


@pytest.mark.asyncio
async def test_redis_async_dbnum(redisdb_async: Redis, redisdb_async_dbnum: Redis) -> None:
    """Check that the dbnum factory argument selects a separate database."""
    await redisdb_async.set("test1", "db0")
    await redisdb_async_dbnum.set("test1", "db4")

    assert await redisdb_async.get("test1") == b"db0"
    assert await redisdb_async_dbnum.get("test1") == b"db4"


@pytest.mark.asyncio
async def test_async_and_sync_share_instance(redisdb_async: Redis, redisdb: SyncRedis) -> None:
    """Check that async and sync client fixtures talk to the same redis instance."""
    await redisdb_async.set("written_by_async", "async")
    redisdb.set("written_by_sync", "sync")

    assert redisdb.get("written_by_async") == b"async"
    assert await redisdb_async.get("written_by_sync") == b"sync"
