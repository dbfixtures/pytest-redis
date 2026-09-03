"""Tests for the behaviour of the redisdb_async fixture factory itself."""

import pytest

from pytest_redis.executor import RedisExecutor


def test_async_fixture_without_pytest_asyncio(pytester: pytest.Pytester) -> None:
    """Check a helpful error is raised when pytest-asyncio is not installed.

    Runs with ``pytest_asyncio`` blanked out.
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


def test_async_fixture_flushes_and_closes(
    pytester: pytest.Pytester, redis_proc: RedisExecutor
) -> None:
    """Check the async fixture flushes the database and closes the client on teardown.

    The nested test reuses redis instance started in this test session.
    """
    # The nested session runs async tests, so it needs pytest-asyncio for real.
    pytest.importorskip("pytest_asyncio", minversion="1.0.0")
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
            pool = used_clients[0].connection_pool
            assert not any(conn.is_connected for conn in pool._available_connections)
            assert pool._in_use_connections == set()
        """
    )
    result = pytester.runpytest_subprocess("-p", "no:cacheprovider", "-p", "no:xdist")
    result.assert_outcomes(passed=3)
