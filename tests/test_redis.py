"""Module containing all tests for pytest-redis."""

import pytest
from pytest import FixtureRequest, Pytester
from redis.client import Redis

from pytest_redis.config import get_config


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


OPTIONS_TEST = """
def test_options(redisdb):
    assert redisdb.config_get("maxmemory") == {"maxmemory": "104857600"}
    assert redisdb.config_get("maxmemory-policy") == {"maxmemory-policy": "allkeys-lru"}
"""


def test_redis_options_from_ini(pytester: Pytester, request: FixtureRequest) -> None:
    """Extra options can be set in the configuration file."""
    pytester.makeini(
        """
        [pytest]
        redis_options =
            maxmemory 100mb
            maxmemory-policy allkeys-lru
        """
    )
    pytester.makepyfile(OPTIONS_TEST)
    result = pytester.runpytest(f"--redis-exec={get_config(request).exec}")
    result.assert_outcomes(passed=1)


def test_redis_options_from_command_line(pytester: Pytester, request: FixtureRequest) -> None:
    """Extra options can be set on the command line, one per --redis-option."""
    pytester.makepyfile(OPTIONS_TEST)
    result = pytester.runpytest(
        f"--redis-exec={get_config(request).exec}",
        "--redis-option",
        "maxmemory 100mb",
        "--redis-option",
        "maxmemory-policy allkeys-lru",
    )
    result.assert_outcomes(passed=1)


def test_redis_options_from_factory(pytester: Pytester, request: FixtureRequest) -> None:
    """Extra options can be passed to the redis_proc factory."""
    pytester.makeconftest(
        """
        from pytest_redis import factories

        redis_proc = factories.redis_proc(
            options=["maxmemory 100mb", "maxmemory-policy allkeys-lru"]
        )
        """
    )
    pytester.makepyfile(OPTIONS_TEST)
    result = pytester.runpytest(f"--redis-exec={get_config(request).exec}")
    result.assert_outcomes(passed=1)


def test_redis_options_command_line_replaces_ini(
    pytester: Pytester, request: FixtureRequest
) -> None:
    """Options given on the command line replace the ones in the configuration file."""
    pytester.makeini(
        """
        [pytest]
        redis_options =
            maxmemory 1mb
        """
    )
    pytester.makepyfile(OPTIONS_TEST)
    result = pytester.runpytest(
        f"--redis-exec={get_config(request).exec}",
        "--redis-option",
        "maxmemory 100mb",
        "--redis-option",
        "maxmemory-policy allkeys-lru",
    )
    result.assert_outcomes(passed=1)


def test_redis_options_factory_replaces_command_line_and_ini(
    pytester: Pytester, request: FixtureRequest
) -> None:
    """Options passed to the factory replace the command line and configuration file ones."""
    pytester.makeini(
        """
        [pytest]
        redis_options =
            maxmemory 1mb
        """
    )
    pytester.makeconftest(
        """
        from pytest_redis import factories

        redis_proc = factories.redis_proc(
            options=["maxmemory 100mb", "maxmemory-policy allkeys-lru"]
        )
        """
    )
    pytester.makepyfile(OPTIONS_TEST)
    result = pytester.runpytest(
        f"--redis-exec={get_config(request).exec}",
        "--redis-option",
        "maxmemory 2mb",
    )
    result.assert_outcomes(passed=1)
