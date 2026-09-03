"""Module containing all tests for pytest-redis async client fixtures."""

import pytest

pytest_asyncio = pytest.importorskip("pytest_asyncio", minversion="1.0.0")

from redis import Redis as SyncRedis  # noqa: E402
from redis.asyncio import Redis  # noqa: E402

import pytest_redis.factories  # noqa: E402
from pytest_redis.executor import RedisExecutor  # noqa: E402

# The async external-redis tests get their own fixed ports, so that they never
# contend for a port with their sync counterparts when the two land on
# different xdist workers.
redis_proc4 = pytest_redis.factories.redis_proc(port=6382)
redis_noproc4 = pytest_redis.factories.redis_noproc(port=6382, startup_timeout=1)
redis_proc5 = pytest_redis.factories.redis_proc(port=6386, password="secretpassword")
redis_noproc5 = pytest_redis.factories.redis_noproc(port=6386, password="secretpassword")

# ``redis_other_proc`` lives in conftest.py, shared with the sync client tests.
redis_otherdb_async = pytest_redis.factories.redisdb_async("redis_other_proc")
redisdb4_async = pytest_redis.factories.redisdb_async("redis_proc4")
redisdb4_noop_async = pytest_redis.factories.redisdb_async("redis_noproc4")
redisdb5_async = pytest_redis.factories.redisdb_async("redis_proc5")
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


def test_async_fixture_flushes_and_closes(
    pytester: pytest.Pytester, redis_proc: RedisExecutor
) -> None:
    """Check the async fixture flushes the database and closes the client on teardown.

    Runs in a nested pytest session so the assertions can observe what happens
    *after* the fixture tore down. The nested session reuses the redis instance
    already started for this test, through a noproc fixture.
    """
    pytester.makeconftest(
        f"""
        import pytest_redis.factories

        redis_noproc_reused = pytest_redis.factories.redis_noproc(port={redis_proc.port})
        redisdb_async_reused = pytest_redis.factories.redisdb_async("redis_noproc_reused")
        """
    )
    pytester.makepyfile(
        """
        import pytest

        used_clients = []


        @pytest.mark.asyncio
        async def test_writes_a_key(redisdb_async_reused):
            used_clients.append(redisdb_async_reused)
            await redisdb_async_reused.set("should_be_flushed", "1")


        @pytest.mark.asyncio
        async def test_key_is_gone(redisdb_async_reused):
            assert await redisdb_async_reused.get("should_be_flushed") is None


        def test_first_client_got_closed():
            # aclose() disconnects the pool it owns, leaving no live connection
            # behind for the closed event loop to trip over.
            pool = used_clients[0].connection_pool
            assert not any(conn.is_connected for conn in pool._available_connections)
            assert pool._in_use_connections == set()
        """
    )
    result = pytester.runpytest_subprocess("-p", "no:cacheprovider", "-p", "no:xdist")
    result.assert_outcomes(passed=3)


def test_async_fixture_without_pytest_asyncio(pytester: pytest.Pytester) -> None:
    """Check a helpful error is raised when pytest-asyncio is not installed.

    Runs in a nested pytest session with ``pytest_asyncio`` blanked out, so the
    unavailable-stub path is exercised without uninstalling anything.
    """
    pytester.makeconftest(
        """
        import pytest_redis.factories.client_async as client_async

        client_async.pytest_asyncio = None
        redisdb_async_stub = client_async.redisdb_async("redis_proc")
        """
    )
    pytester.makepyfile(
        """
        def test_stub(redisdb_async_stub):
            pass
        """
    )
    result = pytester.runpytest_subprocess("-p", "no:cacheprovider", "-p", "no:xdist")
    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*required for async fixtures*"])
