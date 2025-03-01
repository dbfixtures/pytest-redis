CHANGELOG
=========

.. towncrier release notes start

3.1.3 (2024-11-27)
==================

Breaking changes
----------------

- Drop support for Python 3.8


Features
--------

- Mark support for python 3.13


Miscellaneus
------------

- Dropped Redis 6.0 and 7.0 from CI
  Add Redis 7.4 into CI


3.1.2 (2024-06-19)
==================

Bugfixes
--------

- Fix compatibility with pytest < 8 (`#677 <https://github.com/dbfixtures/pytest-redis/issues/677>`__)


3.1.1 (2024-06-10)
==================

Bugfixes
--------

- Fixed redis factories module, where imports from submodule
  on the main `factories` level were removed by linter. (`#679 <https://github.com/dbfixtures/pytest-redis/issues/679>`__)


3.1.0 (2024-06-05)
==================

Features
--------

- Add '--redis-modules' command line option (or 'redis_modules' in .ini file) to specify comma-separated list of Redis extension modules to load (`#656 <https://github.com/dbfixtures/pytest-redis/issues/656>`__)
- Support Python 3.12 (`#673 <https://github.com/dbfixtures/pytest-redis/issues/673>`__)


Miscellaneus
------------

- Adjusted workflows for actions-reuse 2 (`#481 <https://github.com/dbfixtures/pytest-redis/issues/481>`__)
- Migrate pydocstyle and pycodestyle to ruff. And use rstcheck to check rst files. (`#484 <https://github.com/dbfixtures/pytest-redis/issues/484>`__)
- Update code formatting for black 24.1 (`#602 <https://github.com/dbfixtures/pytest-redis/issues/602>`__)
- Drop Pipfile.lock from repository.
  Will rely on a cached in Pipeline or artifact. (`#604 <https://github.com/dbfixtures/pytest-redis/issues/604>`__)
- Drop old install_py test step, that's supposed to install packages for caching purposes. (`#674 <https://github.com/dbfixtures/pytest-redis/issues/674>`__)
- Test against Redis 7.2 (`#675 <https://github.com/dbfixtures/pytest-redis/issues/675>`__)


3.0.2 (2023-04-19)
==================

Bugfixes
--------

- Include py.typed in MANIFEST.in (`#471 <https://github.com/dbfixtures/pytest-redis/issues/471>`__)


3.0.1 (2023-03-27)
==================

Bugfixes
--------

- Fixed packaging LICENSE file. (`#453 <https://github.com/dbfixtures/pytest-redis/issues/453>`__)


3.0.0 (2023-03-24)
==================

Breaking changes
----------------

- Dropped support for Python 3.7 (`#428 <https://github.com/dbfixtures/pytest-redis/issues/428>`__)


Bugfixes
--------

- NoopRedis fixture - used to connecto extenrally set up redis, now properly waits till it's ready to accept connections (`#388 <https://github.com/dbfixtures/pytest-redis/issues/388>`__)


Features
--------

- Use shutilo.where to find redis-server by default (`#374 <https://github.com/dbfixtures/pytest-redis/issues/374>`__)
- Support for Redis 7 (`#391 <https://github.com/dbfixtures/pytest-redis/issues/391>`__)
- Added username and password settings used to connect to the redis instances, set up both internally and externally. (`#404 <https://github.com/dbfixtures/pytest-redis/issues/404>`__)
- Fully type pytest-redis (`#428 <https://github.com/dbfixtures/pytest-redis/issues/428>`__)
- Support python 3.11 (`#437 <https://github.com/dbfixtures/pytest-redis/issues/437>`__)


Miscellaneus
------------

- Added py.typed file (`#422 <https://github.com/dbfixtures/pytest-redis/issues/422>`__)
- Added towncrier to manage newsfragment/CHANGELOG (`#424 <https://github.com/dbfixtures/pytest-redis/issues/424>`__)
- Migrate dependency management to pipenv (`#425 <https://github.com/dbfixtures/pytest-redis/issues/425>`__)
- Moved most of the project's packaging and configuration to pyproject.toml (`#426 <https://github.com/dbfixtures/pytest-redis/issues/426>`__)
- Migrate automerge to a shared workflow based on application token management. (`#427 <https://github.com/dbfixtures/pytest-redis/issues/427>`__)
- Added mypy checks for CI (`#428 <https://github.com/dbfixtures/pytest-redis/issues/428>`__)
- Use tbump instead of bumpversion to manage release process (`#429 <https://github.com/dbfixtures/pytest-redis/issues/429>`__)
- Remove Redis versions older nat 6.0.x from CI as they have reached EOL. (`#445 <https://github.com/dbfixtures/pytest-redis/issues/445>`__)
- Removed the bit hidden ability to select over Redis/StrictRedis client for client fixture.
  For a long time both were same client already. (`#447 <https://github.com/dbfixtures/pytest-redis/issues/447>`__)
- Split bigger code modules into smaller chunks. (`#452 <https://github.com/dbfixtures/pytest-redis/issues/452>`__)


2.4.0
=====

Features
--------

- Import FixtureRequest from pytest, not private _pytest. Require at least pytest 6.2
- Replace tmpdir_factory with tmp_path_factory


2.3.0
=====

Features
--------

- Added datadir configuration that allows to modify the placement of a redis_proc generated files in the specific place.
  This helps overcome the issue with long tmp paths on macosx separately from the temporary path itself.

2.2.0
=====

Features
--------

- Configure redis to listen on specific hostname exclusively using `--bind` parameter.

Misc
----

- rely on `get_port` functionality delivered by `port_for`


2.1.1
=====

Misc
----

- Rise more informative error when the unixsocket is too long. Now the error
  will hint at solution how to overcome it. This might be issue especially on
  MacOS, where the default temp folder is already a long path

2.1.0
=====

Features
--------

- Rely on tmpdir_factory for handling tmpdirs. Now it's cleanup should
  be handled better without much of the leftovers dangling indefinitely
  in the tmp directory.
- Store pidfile in fixture's temporary directory
- Support only python 3.7 and up

Backward incompatibilities
--------------------------

- Dropped `--redis-logsdir` command line option, `redis_logsdir` ini file
  configuration option and `logsdir` fixture factory configuration option.
  Logs will be automatically placed in fixture's temporary directory.
- Dropped `logs_prefix` argument from fixture factory argument

2.0.0
=====

- [feature] ability to properly connect to already existing postgresql server using ``redis_nooproc`` fixture.
- [enhancement] dropped support for python 2.7

1.3.2
=====

- [bugfix] - close file descriptor when reading redis version (by brunsgaard)

1.3.1
=====

- [bugfix] do not run redis explicitly with shell=True

1.3.0
=====

- [enhancement] RedisExecutor now provides attribute with path to unixsocket
- [enhancement] redis client fixture now connects to redis through unixsocket by default
- [enhancement] Version check got moved to executor, to be run just before starting Redis Server
- [feature] ability to configure decode_responses for redis client in command line, pytest.ini or factory argument.
- [bugfix] set decode_responses to False, same as StrictRedis default
- [enhancement] ability to change decode_responses value

1.2.1
=====

- [bugfix] raise specific error in case the redis executable path has been misconfigured or does not exists

1.2.0
=====

- [feature] ability to configure syslog-enabled for redis in command line, pytest.ini or factory argument.
- [feature] ability to configure rdbchecksum for redis in command line, pytest.ini or factory argument.
- [feature] ability to configure rdbcompression for redis in command line, pytest.ini or factory argument.
- [ehnacement] - RedisExecutor handling parameters and their translation to redis values if needed.
- [feature] ability to configure save option for redis in command line, pytest.ini or factory argument.

1.1.1
=====
- [cleanup] removed path.py dependency

1.1.0
=====

- [feature] - migrate usage of getfuncargvalue to getfixturevalue. require at least pytest 3.0.0

1.0.0
=====

- [enhancements] removed the possibility to pass the custom config. No need to include one in package now.
- [enhancements] command line, pytest.ini and fixture factory options for setting custom number of databases in redis
- [enhancements] command line, pytest.ini and fixture factory options for redis log verbosity
- [enhancements] command line, pytest.ini and fixture factory options for modifying connection timeout
- [enhancements] command line and pytest.ini options for modifying executable
- [enhancements] command line and pytest.ini options for modifying host
- [enhancements] command line and pytest.ini options for modifying port
- [enhancements] command line and pytest.ini options for modifying logs directory destination
