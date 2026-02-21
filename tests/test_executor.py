"""Clean executor's tests."""

import socket
from io import StringIO
from typing import Any, Literal

import pytest
import redis
from mirakuru.exceptions import ProcessExitedWithError, TimeoutExpired
from mock import mock
from packaging.version import parse
from port_for import get_port
from pytest import FixtureRequest, TempPathFactory

from pytest_redis.config import get_config
from pytest_redis.exception import RedisMisconfigured, RedisUnsupported, UnixSocketTooLong
from pytest_redis.executor import (
    NoopRedis,
    RedisExecutor,
)
from pytest_redis.executor.process import extract_version


@pytest.mark.parametrize(
    "parameter, config_option, value",
    (
        ({"save": "900 1 300 10"}, "save", "900 1 300 10"),
        ({"save": "900 1"}, "save", "900 1"),
        ({"rdbcompression": True}, "rdbcompression", "yes"),
        ({"rdbcompression": False}, "rdbcompression", "no"),
        ({"rdbchecksum": True}, "rdbchecksum", "yes"),
        ({"rdbchecksum": False}, "rdbchecksum", "no"),
    ),
)
def test_redis_exec_configuration(
    request: FixtureRequest,
    tmp_path_factory: TempPathFactory,
    parameter: dict[str, Any],
    config_option: str,
    value: str,
) -> None:
    """Check if RedisExecutor properly processes configuration options.

    Improperly set options won't be set in redis,
    and we won't be able to read it out of redis.
    """
    config = get_config(request)
    tmpdir = tmp_path_factory.mktemp("pytest-redis-test-test_redis_exec_configuration")
    redis_port = get_port(None)
    assert redis_port
    redis_exec = RedisExecutor(
        executable=config.exec,
        databases=4,
        redis_timeout=config.timeout,
        loglevel=config.loglevel,
        port=redis_port,
        host=config.host,
        startup_timeout=30,
        datadir=tmpdir,
        **parameter,
    )
    with redis_exec:
        redis_client = redis.StrictRedis(redis_exec.host, redis_exec.port, 0)
        assert redis_client.config_get(config_option) == {config_option: value}


@pytest.mark.parametrize(
    "syslog_enabled",
    (True, False),
)
def test_redis_exec(
    request: FixtureRequest, tmp_path_factory: TempPathFactory, syslog_enabled: bool
) -> None:
    """Check if RedisExecutor properly starts with these configuration options.

    Incorrect options won't even start redis.
    """
    config = get_config(request)
    tmpdir = tmp_path_factory.mktemp("pytest-redis-test-test_redis_exec")
    redis_port = get_port(None)
    assert redis_port
    redis_exec = RedisExecutor(
        executable=config.exec,
        databases=4,
        redis_timeout=config.timeout,
        loglevel=config.loglevel,
        port=redis_port,
        host=config.host,
        startup_timeout=30,
        datadir=tmpdir,
        syslog_enabled=syslog_enabled,
    )
    with redis_exec:
        assert redis_exec.running()


@pytest.mark.parametrize(
    "value, redis_value",
    (
        (True, "yes"),
        (1, "yes"),
        ("str", "yes"),
        ("yes", "yes"),
        (False, "no"),
        (0, "no"),
        ("", "no"),
        ("no", "no"),
    ),
)
def test_convert_bool(value: Any, redis_value: Literal["yes", "no"]) -> None:
    """Check correctness of the redis_bool method."""
    # pylint:disable=protected-access
    assert RedisExecutor._redis_bool(value) == redis_value
    # pylint:enable=protected-access


@pytest.mark.parametrize(
    "version",
    (
        "Redis server version 2.4.14 (e9935407:0)",
        "Redis server version 2.4.13 (e0935407:0)"
        "Redis server version 2.5.0 (e9035407:0)"
        "Redis server version 2.3.10 (e9933407:0)",
    ),
)
def test_old_redis_version(
    request: FixtureRequest, tmp_path_factory: TempPathFactory, version: str
) -> None:
    """Test how fixture behaves in case of old redis version."""
    config = get_config(request)
    tmpdir = tmp_path_factory.mktemp("pytest-redis-test-test_old_redis_version")
    with mock.patch("os.popen", lambda *args: StringIO(version)):
        with pytest.raises(RedisUnsupported):
            redis_port = get_port(None)
            assert redis_port
            RedisExecutor(
                config.exec,
                databases=4,
                redis_timeout=config.timeout,
                loglevel=config.loglevel,
                port=redis_port,
                host=config.host,
                startup_timeout=30,
                datadir=tmpdir,
            ).start()


def test_not_existing_redis(request: FixtureRequest, tmp_path_factory: TempPathFactory) -> None:
    """Check handling of misconfigured redis executable path."""
    config = get_config(request)
    tmpdir = tmp_path_factory.mktemp("pytest-redis-test-test_not_existing_redis")
    with pytest.raises(RedisMisconfigured):
        redis_port = get_port(None)
        assert redis_port
        RedisExecutor(
            "/not/redis/here/redis-server",
            databases=4,
            redis_timeout=config.timeout,
            loglevel=config.loglevel,
            port=redis_port,
            host=config.host,
            startup_timeout=30,
            datadir=tmpdir,
        ).start()


def test_too_long_unixsocket(request: FixtureRequest, tmp_path_factory: TempPathFactory) -> None:
    """Check handling of misconfigured redis executable path."""
    config = get_config(request)
    tmpdir = tmp_path_factory.mktemp("x" * 110)
    with pytest.raises(UnixSocketTooLong):
        redis_port = get_port(None)
        assert redis_port
        RedisExecutor(
            config.exec,
            databases=4,
            redis_timeout=config.timeout,
            loglevel=config.loglevel,
            port=redis_port,
            host=config.host,
            startup_timeout=30,
            datadir=tmpdir,
        ).start()


@pytest.mark.parametrize(
    "text,result",
    [
        ("Redis server version 2.4.14 (00000000:0)", "2.4.14"),
        ("Redis server v=2.6.13 sha=00000000:0 malloc=jemalloc-3.3.1 bits=64", "2.6.13"),
        ("1.2.5", "1.2.5"),
        ("Test2.0.5", "2.0.5"),
        ("2.0.5Test", "2.0.5"),
        ("m.n.a 2.4.14", "2.4.14"),
    ],
)
def test_extract_version(text: str, result: str) -> None:
    """Check if the version extracction works correctly."""
    assert extract_version(text) == parse(result)


def test_extract_version_notfound() -> None:
    """Check error raised if version is not found."""
    with pytest.raises(AssertionError):
        extract_version("Test")


def test_noopredis_handles_timeout_when_waiting() -> None:
    """Test handling timeuts by NoopRedis."""
    with mock.patch("pytest_redis.executor.noop.socket", spec=socket) as patched_socket:
        foo = patched_socket.socket.return_value
        socket_mock = foo.__enter__.return_value
        socket_mock.connect.side_effect = TimeoutError()
        noop_redis = NoopRedis(host="localhost", port=12345, startup_timeout=1)
        with pytest.raises(TimeoutExpired):
            noop_redis.start()

        assert not noop_redis.running()
        socket_mock.settimeout.assert_called_with(0.1)
        socket_mock.connect.assert_called()


def test_redis_modules_option(request: FixtureRequest, tmp_path_factory: TempPathFactory) -> None:
    """Set 'module' keyword argument and check command line."""
    config = get_config(request)
    tmpdir = tmp_path_factory.mktemp("pytest-redis-test-test_redis_exec_configuration")
    redis_port = get_port(None)
    assert redis_port

    redis_exec = RedisExecutor(
        executable=config.exec,
        databases=4,
        redis_timeout=config.timeout,
        loglevel=config.loglevel,
        port=redis_port,
        host=config.host,
        startup_timeout=30,
        datadir=tmpdir,
        modules=["nonexistent.so", "nonexistent2.so"],
    )
    try:
        with pytest.raises(
            ProcessExitedWithError, match="--loadmodule nonexistent.so --loadmodule nonexistent2.so"
        ):
            redis_exec.start()

        logfilename = redis_exec.command_parts[redis_exec.command_parts.index("--logfile") + 1]
        with open(logfilename, "r") as logfile:
            logfile_text = logfile.read()
        assert (
            "# Module nonexistent.so failed to load: nonexistent.so: cannot open shared object file"
            in logfile_text
        )
        # cannot check for nonexistent2.so because Redis stops at first invalid module
    finally:
        redis_exec.stop()
