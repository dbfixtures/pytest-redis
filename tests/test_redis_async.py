"""Module containing all tests for pytest-redis."""

import pytest
from redis.asyncio import Redis


@pytest.mark.asyncio
async def test_redis_async(redisdb_async: Redis) -> None:
    """Check that it's actually working on redis database using async client."""
    await redisdb_async.set("test1_async", "test")
    await redisdb_async.set("test2_async", "test")

    test1 = await redisdb_async.get("test1_async")
    assert test1 == b"test"

    test2 = await redisdb_async.get("test2_async")
    assert test2 == b"test"


@pytest.mark.asyncio
async def test_second_redis_async(redisdb_async: Redis, redisdb2_async: Redis) -> None:
    """Check that two redis prorcesses are separate ones."""
    await redisdb_async.set("test1_async", "test")
    await redisdb_async.set("test2_async", "test")
    await redisdb2_async.set("test1_async", "test_other")
    await redisdb2_async.set("test2_async", "test_other")

    assert await redisdb_async.get("test1") == b"test"
    assert await redisdb_async.get("test2") == b"test"

    assert await redisdb2_async.get("test1") == b"test_other"
    assert await redisdb2_async.get("test2") == b"test_other"


@pytest.mark.asyncio
async def test_external_redis(redisdb2_async: Redis, redisdb2_noop_async: Redis) -> None:
    """Check that nooproc connects to the same redis."""
    await redisdb2_async.set("test1", "test_other")
    await redisdb2_async.set("test2", "test_other")

    assert await redisdb2_async.get("test1") == b"test_other"
    assert await redisdb2_async.get("test2") == b"test_other"

    assert await redisdb2_noop_async.get("test1") == b"test_other"
    assert await redisdb2_noop_async.get("test2") == b"test_other"


@pytest.mark.asyncio
async def test_external_redis_auth(redisdb3_async: Redis, redisdb3_noop_async: Redis) -> None:
    """Check that nooproc connects to the same redis."""
    await redisdb3_async.set("test1", "test_other")
    await redisdb3_async.set("test2", "test_other")

    assert await redisdb3_async.get("test1") == b"test_other"
    assert await redisdb3_async.get("test2") == b"test_other"

    assert await redisdb3_noop_async.get("test1") == b"test_other"
    assert await redisdb3_noop_async.get("test2") == b"test_other"
