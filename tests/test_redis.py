"""Module containing all tests for pytest-redis."""

import pytest
from redis.client import Redis


def test_redis(redisdb: Redis) -> None:
    """Check that it's actually working on redis database."""
    redisdb.set("test1", "test")
    redisdb.set("test2", "test")

    test1 = redisdb.get("test1")
    assert test1 == b"test"

    test2 = redisdb.get("test2")
    assert test2 == b"test"


def test_second_redis(redisdb: Redis, redis_otherdb: Redis) -> None:
    """Check that two redis prorcesses are separate ones."""
    redisdb.set("test1", "test")
    redisdb.set("test2", "test")
    redis_otherdb.set("test1", "test_other")
    redis_otherdb.set("test2", "test_other")

    assert redisdb.get("test1") == b"test"
    assert redisdb.get("test2") == b"test"

    assert redis_otherdb.get("test1") == b"test_other"
    assert redis_otherdb.get("test2") == b"test_other"


@pytest.mark.xdist_group(name="redis2")
def test_external_redis(redisdb2: Redis, redisdb2_noop: Redis) -> None:
    """Check that nooproc connects to the same redis."""
    redisdb2.set("test1", "test_other")
    redisdb2.set("test2", "test_other")

    assert redisdb2.get("test1") == b"test_other"
    assert redisdb2.get("test2") == b"test_other"

    assert redisdb2_noop.get("test1") == b"test_other"
    assert redisdb2_noop.get("test2") == b"test_other"


@pytest.mark.xdist_group(name="redis3")
def test_external_redis_auth(redisdb3: Redis, redisdb3_noop: Redis) -> None:
    """Check that nooproc connects to the same redis."""
    redisdb3.set("test1", "test_other")
    redisdb3.set("test2", "test_other")

    assert redisdb3.get("test1") == b"test_other"
    assert redisdb3.get("test2") == b"test_other"

    assert redisdb3_noop.get("test1") == b"test_other"
    assert redisdb3_noop.get("test2") == b"test_other"
