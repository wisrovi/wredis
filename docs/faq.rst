Frequently Asked Questions
==========================

General
-------

What is WRedis?
~~~~~~~~~~~~~~~

WRedis is a production-ready Python library that provides a clean, intuitive interface for interacting with Redis. It offers both synchronous and asynchronous APIs, cache decorators, high-availability support, and comprehensive type hints.

What Python versions are supported?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

WRedis supports Python 3.10, 3.11, 3.12, and 3.13.

Is WRedis production-ready?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes. WRedis v1.0.0 is an LTS (Long-Term Support) release designed for production use. It includes comprehensive test coverage (95%+), type hints, and error handling.

Installation
------------

How do I install WRedis?
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install wredis

For development dependencies:

.. code-block:: bash

   pip install wredis[dev]

What are the dependencies?
~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``redis>=5.0.0`` - Redis Python client
- ``loguru>=0.7.0`` - Logging library

Usage
-----

How do I connect to a remote Redis server?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wredis.hash import RedisHashManager

   manager = RedisHashManager(
       host="redis.example.com",
       port=6379,
       db=0,
       verbose=True,
   )

How do I use WRedis with FastAPI?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the async API for non-blocking operations:

.. code-block:: python

   from fastapi import FastAPI
   from wredis.async_api.hash import AsyncRedisHashManager

   app = FastAPI()
   manager = AsyncRedisHashManager()

   @app.get("/users/{user_id}")
   async def get_user(user_id: int):
       return await manager.read_hash(f"user:{user_id}", "profile")

How do I implement caching?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``@cache`` decorator:

.. code-block:: python

   from wredis.decorators import cache

   @cache(ttl=300, prefix="api:users")
   def get_user(user_id: int) -> dict:
       # Expensive operation
       return {"id": user_id, "name": "Alice"}

How do I handle errors?
~~~~~~~~~~~~~~~~~~~~~~~

WRedis provides custom exceptions:

.. code-block:: python

   from wredis._exceptions import WRedisError, RedisConnectionError, CacheError

   try:
       manager.create_hash("key", "field", "value")
   except RedisConnectionError as e:
       print(f"Connection failed: {e}")
   except WRedisError as e:
       print(f"WRedis error: {e}")

High Availability
-----------------

How do I set up Sentinel?
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wredis.ha import SentinelRedisManager

   sentinel = SentinelRedisManager(
       sentinel_nodes=[
           ("sentinel-1.example.com", 26379),
           ("sentinel-2.example.com", 26379),
       ],
       service_name="mymaster",
   )

   master = sentinel.get_master()

How do I connect to a Redis Cluster?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wredis.ha import ClusterRedisManager

   cluster = ClusterRedisManager(
       startup_nodes=[
           ("cluster-1.example.com", 7000),
           ("cluster-2.example.com", 7001),
       ],
   )

   client = cluster.redis_client

Performance
-----------

How can I improve performance?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Use pipelines** - Batch multiple commands together
2. **Enable connection pooling** - Reuse connections across operations
3. **Use async API** - Non-blocking operations for high-concurrency scenarios
4. **Implement caching** - Reduce redundant database queries
5. **Monitor memory usage** - Set appropriate TTLs for keys

What is the overhead of WRedis?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

WRedis adds minimal overhead compared to direct Redis commands. The abstraction layer provides error handling, logging, and type safety with negligible performance impact.

Testing
-------

How do I run tests?
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/ --cov=wredis

How do I run integration tests?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration tests require a running Redis server:

.. code-block:: bash

   pytest tests/integration/ --cov=wredis

Troubleshooting
---------------

Connection refused error
~~~~~~~~~~~~~~~~~~~~~~~~

Ensure Redis is running and accessible:

.. code-block:: bash

   redis-cli ping

If using Docker:

.. code-block:: bash

   docker run -d -p 6379:6379 redis:latest

Serialization errors
~~~~~~~~~~~~~~~~~~~~

Ensure values are JSON-serializable when using hash operations with dictionaries.

Cache not working
~~~~~~~~~~~~~~~~~

1. Verify Redis connection
2. Check TTL values (use positive integers)
3. Ensure key prefixes are consistent
4. Verify cache invalidation patterns match cache key patterns

Where can I get help?
---------------------

- **GitHub Issues**: https://github.com/wisrovi/wredis/issues
- **Contributing Guide**: See the CONTRIBUTING.md file in the repository
- **Author**: `wisrovi on LinkedIn <https://es.linkedin.com/in/wisrovi-rodriguez>`_
