"""Tests main conftest file."""

import warnings

import pytest_redis.factories

pytest_plugins = ["pytester"]

warnings.filterwarnings(
    "error", category=DeprecationWarning, module="(_pytest|pytest|redis|path|mirakuru).*"
)

redis_other_proc = pytest_redis.factories.redis_proc()

redis_proc2 = pytest_redis.factories.redis_proc(port=6381)
redis_noproc2 = pytest_redis.factories.redis_noproc(port=6381, startup_timeout=1)
redis_proc3 = pytest_redis.factories.redis_proc(port=6385, password="secretpassword")
redis_noproc3 = pytest_redis.factories.redis_noproc(port=6385, password="secretpassword")

# The async external-redis tests get their own fixed ports, so that they never
# contend for a port with their sync counterparts when the two land on
# different xdist workers.
redis_proc4 = pytest_redis.factories.redis_proc(port=6382)
redis_noproc4 = pytest_redis.factories.redis_noproc(port=6382, startup_timeout=1)
redis_proc5 = pytest_redis.factories.redis_proc(port=6386, password="secretpassword")
redis_noproc5 = pytest_redis.factories.redis_noproc(port=6386, password="secretpassword")

redis_otherdb = pytest_redis.factories.redisdb("redis_other_proc")
redisdb2 = pytest_redis.factories.redisdb("redis_proc2")
redisdb2_noop = pytest_redis.factories.redisdb("redis_noproc2")
redisdb3 = pytest_redis.factories.redisdb("redis_proc3")
redisdb3_noop = pytest_redis.factories.redisdb("redis_noproc3")

redis_otherdb_async = pytest_redis.factories.redisdb_async("redis_other_proc")
redisdb4_async = pytest_redis.factories.redisdb_async("redis_proc4")
redisdb4_noop_async = pytest_redis.factories.redisdb_async("redis_noproc4")
redisdb5_async = pytest_redis.factories.redisdb_async("redis_proc5")
redisdb5_noop_async = pytest_redis.factories.redisdb_async("redis_noproc5")
redisdb_async_decode = pytest_redis.factories.redisdb_async("redis_proc", decode=True)
redisdb_async_dbnum = pytest_redis.factories.redisdb_async("redis_proc", dbnum=4)
