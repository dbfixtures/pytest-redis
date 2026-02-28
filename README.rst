.. image:: https://raw.githubusercontent.com/dbfixtures/pytest-redis/master/logo.png
    :width: 100px
    :height: 100px

pytest-redis
============

.. image:: https://img.shields.io/pypi/v/pytest-redis.svg
    :target: https://pypi.python.org/pypi/pytest-redis/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/wheel/pytest-redis.svg
    :target: https://pypi.python.org/pypi/pytest-redis/
    :alt: Wheel Status

.. image:: https://img.shields.io/pypi/pyversions/pytest-redis.svg
    :target: https://pypi.python.org/pypi/pytest-redis/
    :alt: Supported Python Versions

.. image:: https://img.shields.io/pypi/l/pytest-redis.svg
    :target: https://pypi.python.org/pypi/pytest-redis/
    :alt: License

What is this?
=============

This is a pytest plugin, that enables you to test your code that relies on a running Redis database.
It allows you to specify additional fixtures for Redis process and client.



.. image:: https://raw.githubusercontent.com/dbfixtures/pytest-redis/main/docs/images/architecture.svg
    :alt: Project Architecture Diagram
    :align: center


How to use
==========

Plugin contains three fixtures

* **redisdb** - This is a redis client fixture. It constructs a redis client and cleans redis database after the test.
    It relies on redis_proc fixture, and as such the redis process is started at the very beginning of the first test
    using this fixture, and stopped after the last test finishes.
* **redis_proc** - session scoped fixture, that starts Redis instance at it's first use and stops at the end of the tests.
* **redis_nooproc** - a nooprocess fixture, that's connecting to already running redis

Simply include one of these fixtures into your tests fixture list.

.. code-block:: python

    #
    def test_redis(redisdb):
        """Check that it's actually working on redis database."""
        redisdb.set('test1', 'test')
        redisdb.set('test2', 'test')

        my_functionality = MyRedisBasedComponent()
        my_functionality.do_something()
        assert my_functionality.did_something

        assert redisdb.get("did_it") == 1

For the example above works like following:

1. pytest runs tests
2. redis_proc starts redis database server
3. redisdb creates client connection to the server
4. test itself runs and finishes
5. redisdb cleans up the redis
6. redis_proc stops server (if that was the last test using it)
7. pytest ends running tests

You can also create additional redis client and process fixtures if you'd need to:


.. code-block:: python

    from pytest_redis import factories

    redis_my_proc = factories.redis_proc(port=None)
    redis_my = factories.redisdb('redis_my_proc')

    def test_my_redis(redis_my):
        """Check that it's actually working on redis database."""
        redis_my.set('test1', 'test')
        redis_my.set('test2', 'test')

        my_functionality = MyRedisBasedComponent()
        my_functionality.do_something()
        assert my_functionality.did_something

        assert redis_my.get("did_it") == 1

.. note::

    Each Redis process fixture can be configured in a different way than the others through the fixture factory arguments.


Connecting to already existing redis database
---------------------------------------------

Some projects are using already running redis servers (ie on docker instances).
In order to connect to them, one would be using the ``redis_nooproc`` fixture.

.. code-block:: python

    redis_external = factories.redisdb('redis_nooproc')

    def test_redis(redis_external):
        """Check that it's actually working on redis database."""
        redis_external.set('test1', 'test')
        redis_external.set('test2', 'test')

        my_functionality = MyRedisBasedComponent()
        my_functionality.do_something()
        assert my_functionality.did_something

        assert redis_external.get("did_it") == 1

Standard configuration options apply to it. Note that the `modules` configuration option
has no effect with the ``redis_nooproc`` fixture, it is the responsibility of the already
running redis server to be properly started with extension modules, if needed.

By default the ``redis_nooproc`` fixture would connect to Redis
instance using **6379** port attempting to make a successful socket
connection within **15 seconds**. The fixture will block your test run
within this timeout window. You can overwrite the timeout like so:


.. code-block:: python

    # set the blocking wait to 5 seconds
    redis_external = factories.redis_noproc(timeout=5)

    def test_redis(redis_external):
        """Check that it's actually working on redis database."""
        redis_external.set('test1', 'test')
        # etc etc

These are the configuration options that are working on all levels with the ``redis_nooproc`` fixture:

Configuration
=============

You can define your settings in three ways, it's fixture factory argument, command line option and pytest.ini configuration option.
You can pick which you prefer, but remember that these settings are handled in the following order:

    * ``Fixture factory argument``
    * ``Command line option``
    * ``Configuration option in your pytest.ini file``

.. list-table:: Configuration options
   :header-rows: 1

   * - Redis server option
     - Fixture factory argument
     - Command line option
     - pytest.ini option
     - Noop process fixture
     - Default
   * - executable
     - executable
     - --redis-exec
     - redis_exec
     - -
     - Look in PATH for redis-server via shutil.which
   * - host
     - host
     - --redis-host
     - redis_host
     - host
     - 127.0.0.1
   * - port
     - port
     - --redis-port
     - redis_port
     - port
     - random
   * - Free port search count
     - port_search_count
     - --redis-port-search-count
     - redis_port_search_count
     - -
     - 5
   * - username
     - username
     - --redis-username
     - redis_username
     - username
     - None
   * - password
     - password
     - --redis-password
     - redis_password
     - password
     - None
   * - connection timeout
     - timeout
     - --redis-timeout
     - redis_timeout
     - -
     - 30
   * - number of databases
     - db_count
     - --redis-db-count
     - redis_db_count
     - -
     - 8
   * - Whether to enable logging to the system logger
     - syslog
     - --redis-syslog
     - redis_syslog
     - -
     - False
   * - Redis log verbosity level
     - loglevel
     - --redis-loglevel
     - redis_loglevel
     - -
     - notice
   * - Compress dump files
     - compress
     - --redis-compress
     - redis_compress
     - -
     - True
   * - Add checksum to RDB files
     - checksum
     - --redis-rdbcompress
     - redis_rdbchecksum
     - -
     - False
   * - Save configuration
     - save
     - --redis-save
     - redis_save
     - -
     - ""
   * - Redis test instance data directory path
     - datadir
     - --redis-datadir
     - redis_datadir
     - -
     - ""
   * - Redis test instance extension module(s) path
     - modules (list of paths)
     - --redis-modules (comma-separated string)
     - redis_modules (comma-separated string)
     - -
     - ""

Example usage:

* pass it as an argument in your own fixture

.. code-block:: python

    redis_proc = factories.redis_proc(port=8888)

* use ``--redis-port`` command line option when you run your tests

.. code-block:: bash

    py.test tests --redis-port=8888


* specify your port as ``redis_port`` in your ``pytest.ini`` file.

    To do so, put a line like the following under the ``[pytest]`` section of your ``pytest.ini``:

.. code-block:: ini

    [pytest]
    redis_port = 8888

Options below are for configuring redis client fixture.

+---------------------+--------------------------+---------------------+-------------------+---------+
| Redis client option | Fixture factory argument | Command line option | pytest.ini option | Default |
+=====================+==========================+=====================+===================+=========+
| decode_response     | decode                   | --redis-decode      | redis_decode      | False   |
+---------------------+--------------------------+---------------------+-------------------+---------+

Release
=======

Install pipenv and --dev dependencies first, Then run:

.. code-block:: bash

    pipenv run tbump [NEW_VERSION]
