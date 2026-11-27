"""Redis executor."""

from pytest_redis.executor.noop import NoopRedis
from pytest_redis.executor.process import RedisExecutor

__all__ = ("NoopRedis", "RedisExecutor")
