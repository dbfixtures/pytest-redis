"""Config loading helpers."""

from dataclasses import dataclass
from typing import cast

from _pytest.fixtures import FixtureRequest


@dataclass
class RedisConfig:
    """Redis configuration options."""

    host: str
    port: int | None
    port_search_count: int
    username: str
    password: str
    exec: str
    timeout: int
    loglevel: str
    db_count: int
    save: str
    compression: bool
    rdbchecksum: bool
    syslog: bool
    decode: bool
    datadir: str
    modules: list[str]
    options: list[str]


def get_config(request: FixtureRequest) -> RedisConfig:
    """Return a RedisConfig with config options."""

    def get_conf_option(option: str) -> object:
        option_name = "redis_" + option
        return request.config.getoption(option_name) or request.config.getini(option_name)

    port = cast(int | str | None, get_conf_option("port"))
    raw_modules = cast(str | None, get_conf_option("modules"))
    if raw_modules:
        modules = raw_modules.split(",")
    else:
        modules = []
    return RedisConfig(
        host=cast(str, get_conf_option("host")),
        port=int(port) if port else None,
        port_search_count=int(cast(int | str, get_conf_option("port_search_count"))),
        username=cast(str, get_conf_option("username")),
        password=cast(str, get_conf_option("password")),
        exec=cast(str, get_conf_option("exec")),
        timeout=int(cast(int | str, get_conf_option("timeout"))),
        loglevel=cast(str, get_conf_option("loglevel")),
        db_count=int(cast(int | str, get_conf_option("db_count"))),
        save=cast(str, get_conf_option("save")),
        compression=bool(get_conf_option("compression")),
        rdbchecksum=bool(get_conf_option("rdbchecksum")),
        syslog=bool(get_conf_option("syslog")),
        decode=bool(get_conf_option("decode")),
        datadir=cast(str, get_conf_option("datadir")),
        modules=modules,
        options=cast(list[str] | None, get_conf_option("options")) or [],
    )
