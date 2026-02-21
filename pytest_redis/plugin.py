# Copyright (C) 2013 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of pytest-redis.

# pytest-redis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pytest-redis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pytest-redis.  If not, see <http://www.gnu.org/licenses/>.
"""Plugin configuration module for pytest-redis."""

from shutil import which

from pytest import Parser

import pytest_redis.factories.client
import pytest_redis.factories.noproc
import pytest_redis.factories.proc

# pylint:disable=invalid-name
_help_exec = "Redis server executable"
_help_host = "Host at which Redis will accept connections"
_help_port = "Port at which Redis will accept connections"
_help_port_search_count = "Number of times pytest-redis will search for a free port"
_help_username = "Username used to authenticate to Redis"
_help_password = "Password used to authenticate to Redis"
_help_timeout = "Client's connection timeout in seconds"
_help_loglevel = "Redis log verbosity level"
_help_db_count = "Number of redis databases"
_help_compress = "Turn on redis dump files compression."
_help_rdbchecksum = "Whether to add checksum to the rdb files"
_help_syslog = "Whether to enable logging to the system logger"
_help_save = "Redis persistance frequency configuration - seconds keys"
_help_decode = (
    "Client: to decode response or not. See redis.StrictRedis decode_response client parameter."
)
_help_datadir = "Directory where test Redis instance data files will be stored"
_help_modules = "Comma separated list of paths to Redis extension modules to be loaded at startup"


def pytest_addoption(parser: Parser) -> None:
    """Define configuration options."""
    parser.addini(name="redis_exec", help=_help_exec, default=which("redis-server"))
    parser.addini(name="redis_host", help=_help_host, default="127.0.0.1")
    parser.addini(
        name="redis_port",
        help=_help_port,
        default=None,
    )
    parser.addini(
        name="redis_port_search_count", type="int", help=_help_port_search_count, default=5
    )
    parser.addini(
        name="redis_username",
        help=_help_username,
        default=None,
    )
    parser.addini(
        name="redis_password",
        help=_help_password,
        default=None,
    )
    parser.addini(
        name="redis_timeout",
        help=_help_timeout,
        default=30,
    )
    parser.addini(
        name="redis_loglevel",
        help=_help_loglevel,
        default="notice",
    )
    parser.addini(
        name="redis_db_count",
        help=_help_db_count,
        default=8,
    )
    parser.addini(
        name="redis_save",
        help=_help_save,
        default=None,
    )
    parser.addini(name="redis_compression", type="bool", help=_help_compress)
    parser.addini(name="redis_rdbchecksum", type="bool", help=_help_rdbchecksum)
    parser.addini(name="redis_syslog", type="bool", help=_help_syslog)
    parser.addini(name="redis_decode", type="bool", help=_help_decode, default=False)
    parser.addini(name="redis_datadir", help=_help_datadir, default=None)
    parser.addini(name="redis_modules", help=_help_modules, default=None)

    parser.addoption(
        "--redis-exec",
        action="store",
        dest="redis_exec",
        help=_help_exec,
    )
    parser.addoption(
        "--redis-host",
        action="store",
        dest="redis_host",
        help=_help_host,
    )
    parser.addoption("--redis-port", action="store", dest="redis_port", help=_help_port)
    parser.addoption(
        "--redis-port-search-count",
        action="store",
        type=int,
        dest="redis_port_search_count",
        help=_help_port_search_count,
    )
    parser.addoption("--redis-username", action="store", dest="redis_username", help=_help_username)
    parser.addoption("--redis-password", action="store", dest="redis_password", help=_help_password)
    parser.addoption("--redis-timeout", action="store", dest="redis_timeout", help=_help_timeout)
    parser.addoption("--redis-loglevel", action="store", dest="redis_loglevel", help=_help_loglevel)
    parser.addoption("--redis-db-count", action="store", dest="redis_db_count", help=_help_db_count)
    parser.addoption("--redis-save", action="store", dest="redis_save", help=_help_save)
    parser.addoption(
        "--redis-compression", action="store_true", dest="redis_compression", help=_help_compress
    )
    parser.addoption(
        "--redis-rdbchecksum", action="store_true", dest="redis_rdbchecksum", help=_help_rdbchecksum
    )
    parser.addoption("--redis-syslog", action="store_true", dest="redis_syslog", help=_help_syslog)
    parser.addoption(
        "--redis-client-decode", action="store_true", dest="redis_decode", help=_help_decode
    )
    parser.addoption("--redis-datadir", action="store", dest="redis_datadir", help=_help_datadir)
    parser.addoption("--redis-modules", action="store", dest="redis_modules", help=_help_modules)


redis_proc = pytest_redis.factories.proc.redis_proc()
redis_nooproc = pytest_redis.factories.noproc.redis_noproc()
redisdb = pytest_redis.factories.client.redisdb("redis_proc")
# pylint:enable=invalid-name
