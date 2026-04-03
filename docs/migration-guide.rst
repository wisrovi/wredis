========================
Migration Guide: v0.x to v1.0.0 LTS
========================

This guide covers everything you need to know when upgrading from wredis 0.x to
1.0.0 LTS. The 1.0.0 release is a major overhaul that introduces a new exception
model, a completely rewritten async API, new modules, cache decorators, and high
availability support.

.. contents:: Table of Contents
   :depth: 3
   :backlinks: top

.. note::
   wredis 1.0.0 requires **Python 3.10+**. Python 3.8 and 3.9 are no longer
   supported.

==================
Breaking Changes
==================

1. Exception Handling No Longer Silent
======================================

**Before (v0.x):** Operations that failed logged errors silently via
``logger.error`` and returned ``None``, ``0``, or empty collections. This made
it impossible for callers to distinguish between a legitimate empty result and
a failed operation.

**After (v1.0.0):** Operations raise specific, typed exceptions. Silent failures
are eliminated.

.. list-table:: Exception Hierarchy
   :header-rows: 1
   :widths: 25 75

   * - Exception
     - Raised When
   * - ``WRedisError``
     - Base class for all wredis exceptions
   * - ``ValidationError``
     - Input validation fails (empty keys, invalid TTL, bad scores)
   * - ``OperationError``
     - A Redis operation fails after all retries are exhausted
   * - ``SerializationError``
     - JSON serialization or deserialization fails
   * - ``CacheError``
     - Cache read/write/invalidation fails
   * - ``PubSubError``
     - Pub/Sub operations fail
   * - ``QueueError``
     - Queue operations fail
   * - ``StreamError``
     - Stream operations fail
   * - ``TransactionError``
     - Transaction fails (e.g., WATCH conflict)
   * - ``SentinelError``
     - Sentinel connection or discovery fails
   * - ``ClusterError``
     - Cluster connection or routing fails

Before::

    # v0.x - silent failure, returns None
    result = manager.get_from_queue("my_queue")
    if result is None:
        # Was the queue empty? Or did the operation fail?
        pass

After::

    # v1.0.0 - explicit exception
    from wredis._exceptions import QueueError, ValidationError

    try:
        result = manager.consume("my_queue")
    except QueueError as e:
        # Operation genuinely failed
        logger.error(f"Queue operation failed: {e}")
    except ValidationError as e:
        # Bad input
        logger.error(f"Invalid input: {e}")

2. Async API Completely Rewritten
=================================

**Before (v0.x):** The async API used ``concurrent.futures.ThreadPoolExecutor``
to wrap synchronous calls. This was not true asynchrony and introduced thread
overhead, GIL contention, and unpredictable behavior under load.

**After (v1.0.0):** The async API is built on ``redis.asyncio`` with real
``asyncio`` tasks. All I/O is non-blocking.

Before::

    # v0.x - threaded wrapper (fake async)
    from wredis.async_api import AsyncRedisQueueManager

    manager = AsyncRedisQueueManager()  # spun up a ThreadPoolExecutor
    result = await manager.consume("my_queue")  # blocking call in a thread

After::

    # v1.0.0 - real asyncio
    from wredis.async_api import AsyncRedisQueueManager

    async with AsyncRedisQueueManager() as manager:
        result = await manager.consume("my_queue")  # true non-blocking I/O

3. Connection Pooling Is Now Explicit
=====================================

**Before (v0.x):** Each manager created its own internal ``redis.StrictRedis``
client with implicit connection settings. There was no shared pool abstraction.

**After (v1.0.0):** All managers inherit from ``BaseManager`` (sync) or
``AsyncBaseManager`` (async), which manage an explicit
``redis.ConnectionPool``. Connection parameters are standardized across all
managers.

Before::

    # v0.x - each manager created its own client
    hash_mgr = RedisHashManager(host="localhost", port=6379)
    queue_mgr = RedisQueueManager(host="localhost", port=6379)
    # Two separate connections, no pooling

After::

    # v1.0.0 - explicit connection pooling via BaseManager
    hash_mgr = RedisHashManager(host="localhost", port=6379, max_connections=20)
    queue_mgr = RedisQueueManager(host="localhost", port=6379, max_connections=20)
    # Each manager has its own pool with configurable size

4. Minimum Python Version Is 3.10
=================================

Python 3.8 and 3.9 have reached end-of-life. wredis 1.0.0 uses type hints and
syntax features (union types with ``|``, ``collections.abc.Callable``) that
require Python 3.10+.

5. Build System Changed to Hatchling
=====================================

``setup.py`` has been removed. All build configuration lives in
``pyproject.toml`` using hatchling. If you install from source, run::

    pip install -e .

instead of ``python setup.py install``.

====================
Deprecation Notices
====================

The following patterns and behaviors from v0.x are deprecated and will be
removed in a future 1.x release:

- **Silent error returns** (``None``, ``0``, ``[]`` on failure) -- update your
  code to catch the appropriate exception types.
- **Thread-based async** -- the old ``ThreadPoolExecutor`` wrapping has been
  entirely removed. There is no backward-compatible shim.
- **Implicit connection creation** -- managers no longer accept bare
  ``redis.Redis`` instances. Use the ``BaseManager`` constructor parameters.

===============================
New Features in v1.0.0
===============================

1. New Modules: Geo, HyperLogLog, Pipeline, Transaction
=======================================================

Four new modules are available in both sync and async variants.

Geo Manager
-----------

Store and query geographic data with Redis GEO commands.

.. code-block:: python

    from wredis.geo import RedisGeoManager

    geo = RedisGeoManager()
    geo.add_location("cities", "Paris", 2.3522, 48.8566)
    geo.add_location("cities", "London", -0.1276, 51.5074)

    distance = geo.get_distance("cities", "Paris", "London", unit="km")
    nearby = geo.search_nearby("cities", 2.3522, 48.8566, radius=100, unit="km")

Async variant::

    from wredis.async_api import AsyncRedisGeoManager

    async with AsyncRedisGeoManager() as geo:
        await geo.add_location("cities", "Paris", 2.3522, 48.8566)
        nearby = await geo.search_nearby("cities", 2.3522, 48.8566, radius=100)

HyperLogLog Manager
-------------------

Probabilistic cardinality counting.

.. code-block:: python

    from wredis.hyperloglog import RedisHyperLogLogManager

    hll = RedisHyperLogLogManager()
    hll.add("visitors", "user_1", "user_2", "user_3")
    count = hll.count("visitors")

    hll.merge("all_visitors", "visitors_day1", "visitors_day2")

Pipeline Manager
----------------

Batch multiple commands into a single round-trip.

.. code-block:: python

    from wredis.async_api import AsyncRedisPipelineManager

    async with AsyncRedisPipelineManager() as pipe:
        commands = [
            ("set", ["key1", "value1"]),
            ("set", ["key2", "value2"]),
            ("get", ["key1"]),
        ]
        results = await pipe.execute_commands(commands)

Transaction Manager
-------------------

Atomic operations with WATCH/MULTI/EXEC semantics.

.. code-block:: python

    from wredis.async_api import AsyncRedisTransactionManager

    async with AsyncRedisTransactionManager() as txn:
        ok = await txn.set_if_not_exists("lock:resource", "held", ttl=60)
        counter = await txn.increment_atomic("page_views")

2. Cache Decorators with Metrics
================================

The new ``wredis.decorators`` module provides ``@cache``, ``@async_cache``,
``@invalidate_cache``, and ``clear_cache`` with built-in ``CacheMetrics``
tracking.

.. code-block:: python

    from wredis.decorators import cache, CacheMetrics

    metrics = CacheMetrics()

    @cache(ttl=300, prefix="myapp", metrics=metrics)
    def expensive_query(user_id: int) -> dict:
        # This runs only on cache miss
        return db.fetch_user(user_id)

    result = expensive_query(42)
    print(metrics)  # CacheMetrics(hits=0, misses=1, errors=0, hit_rate=0.0%)

    result = expensive_query(42)
    print(metrics)  # CacheMetrics(hits=1, misses=1, errors=0, hit_rate=50.0%)

Async version for FastAPI::

    from wredis.decorators import async_cache

    @async_cache(ttl=600, prefix="api")
    async def get_user_profile(user_id: int) -> dict:
        return await db.fetch_profile(user_id)

Cache invalidation::

    from wredis.decorators import invalidate_cache

    @invalidate_cache(pattern="myapp:*")
    def update_user(user_id: int, data: dict) -> None:
        db.update_user(user_id, data)
        # All keys matching "myapp:*" are deleted after this function runs

3. BaseManager and AsyncBaseManager
====================================

All sync managers now inherit from ``BaseManager``, which provides:

- **Connection pooling** via ``redis.ConnectionPool``
- **Health checks** via ``health_check()``
- **Retry logic** via ``@retry`` decorator with exponential backoff
- **Key validation** via ``validate_key()``
- **Context manager** support (``with`` statement)

.. code-block:: python

    from wredis.hash import RedisHashManager

    # Context manager usage
    with RedisHashManager() as mgr:
        if mgr.health_check():
            mgr.set_json("user:1", {"name": "Alice", "age": 30})

    # Manual lifecycle
    mgr = RedisHashManager(max_connections=20, socket_timeout=10.0)
    try:
        mgr.health_check()
        mgr.set_json("user:1", {"name": "Alice"})
    finally:
        mgr.close()

Async variant::

    from wredis.async_api import AsyncRedisHashManager

    async with AsyncRedisHashManager() as mgr:
        alive = await mgr.health_check()
        await mgr.set_json("user:1", {"name": "Alice"})

4. High Availability: Sentinel and Cluster
==========================================

Sentinel
--------

Automatic failover with Redis Sentinel.

.. code-block:: python

    from wredis.ha import SentinelRedisManager

    sentinel = SentinelRedisManager(
        sentinel_nodes=[
            ("sentinel-1.example.com", 26379),
            ("sentinel-2.example.com", 26379),
            ("sentinel-3.example.com", 26379),
        ],
        service_name="mymaster",
    )

    master = sentinel.get_master()
    master.set("key", "value")

    master_address = sentinel.discover_master()
    slaves = sentinel.discover_slaves()

Cluster
-------

Distributed operations across a Redis Cluster.

.. code-block:: python

    from wredis.ha import ClusterRedisManager

    cluster = ClusterRedisManager(
        startup_nodes=[
            ("node-1.example.com", 7000),
            ("node-2.example.com", 7001),
            ("node-3.example.com", 7002),
        ],
        password="secret",
    )

    state = cluster.get_cluster_state()  # "ok" or "fail"
    nodes = cluster.get_nodes()

5. Internal Modules: _serializer, _validation, _retry
=====================================================

These modules are used internally by managers but are also available for
direct use.

Serializer::

    from wredis._serializer import serialize, deserialize
    from wredis._exceptions import SerializationError

    try:
        data = serialize({"key": "value", "nested": [1, 2, 3]})
        obj = deserialize(data)
    except SerializationError as e:
        logger.error(f"Serialization failed: {e}")

Validation::

    from wredis._validation import validate_key, validate_ttl, validate_score
    from wredis._exceptions import ValidationError

    try:
        validate_key("user:123")
        validate_ttl(3600)
        validate_score(42.5)
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")

Retry::

    from wredis._retry import retry, async_retry

    @retry(max_attempts=5, delay=0.5, backoff=2.0)
    def flaky_operation():
        # Retries up to 5 times with exponential backoff
        return external_api.call()

    @async_retry(max_attempts=3, delay=0.1)
    async def async_flaky_operation():
        return await external_async_api.call()

=======================
Step-by-Step Migration Checklist
=======================

Follow these steps in order to migrate your project.

Phase 1: Preparation
====================

1. **Upgrade to Python 3.10+**

   Verify your runtime version::

       python --version  # Must be 3.10 or higher

2. **Pin your current version**

   Before upgrading, pin your current version in ``requirements.txt`` or
   ``pyproject.toml`` so you can roll back if needed::

       wredis==0.1.2

3. **Review your error-handling code**

   Search your codebase for patterns where you check for ``None``, ``0``, or
   empty lists as error indicators. These will need to be updated to use
   ``try/except`` blocks.

Phase 2: Upgrade
================

4. **Install wredis 1.0.0**

   ::

       pip install wredis==1.0.0

5. **Update imports**

   The following imports remain unchanged::

       from wredis import (
           RedisBitmapManager,
           RedisHashManager,
           RedisPubSubManager,
           RedisQueueManager,
           RedisSetManager,
           RedisSortedSetManager,
           RedisStreamManager,
       )

   New imports to adopt as needed::

       from wredis.geo import RedisGeoManager
       from wredis.hyperloglog import RedisHyperLogLogManager
       from wredis.ha import SentinelRedisManager, ClusterRedisManager
       from wredis.decorators import cache, async_cache, CacheMetrics
       from wredis._exceptions import (
           WRedisError,
           ValidationError,
           OperationError,
           CacheError,
           QueueError,
           StreamError,
           PubSubError,
       )

   Async imports::

       from wredis.async_api import (
           AsyncRedisBitmapManager,
           AsyncRedisHashManager,
           AsyncRedisPubSubManager,
           AsyncRedisQueueManager,
           AsyncRedisSetManager,
           AsyncRedisSortedSetManager,
           AsyncRedisStreamManager,
           AsyncRedisGeoManager,
           AsyncRedisHyperLogLogManager,
           AsyncRedisPipelineManager,
           AsyncRedisTransactionManager,
       )

6. **Replace silent error checks with try/except**

   Before::

       result = queue_mgr.consume("tasks")
       if result is None:
           logger.error("Failed to consume from queue")

   After::

       from wredis._exceptions import QueueError

       try:
           result = queue_mgr.consume("tasks")
       except QueueError as e:
           logger.error(f"Queue consume failed: {e}")
           raise

7. **Adopt context managers for resource cleanup**

   Before::

       mgr = RedisHashManager()
       try:
           mgr.set_json("key", value)
       finally:
           mgr.redis_client.close()

   After::

       with RedisHashManager() as mgr:
           mgr.set_json("key", value)

8. **Migrate async code to real asyncio**

   If you used the old async API, rewrite your code to use the new
   ``redis.asyncio``-based managers. The method signatures are largely the
   same, but the underlying implementation is now truly asynchronous.

   Before::

       # v0.x - threaded
       mgr = AsyncRedisQueueManager()
       result = await mgr.consume("tasks")

   After::

       # v1.0.0 - real asyncio
       async with AsyncRedisQueueManager() as mgr:
           result = await mgr.consume("tasks")

Phase 3: Verification
=====================

9. **Run health checks on all connections**

   Add ``health_check()`` calls during application startup to verify
   connectivity before serving traffic::

       with RedisHashManager() as mgr:
           assert mgr.health_check(), "Redis is not reachable"

10. **Run your test suite**

    Ensure all tests pass. Pay special attention to tests that previously
    asserted on ``None`` or empty results from failed operations -- these
    should now assert on raised exceptions instead.

11. **Enable verbose logging during rollout**

    Set ``verbose=True`` (the default) on all managers during the initial
    rollout to get detailed operational logs. Once stable, you can disable
    verbose mode in production.

================
Common Pitfalls
================

Pitfall 1: Catching the Wrong Exception
=======================================

Do not catch bare ``Exception``. Catch the specific wredis exception types
so you can distinguish between validation errors, operational errors, and
network failures.

.. code-block:: python

    # Bad
    try:
        mgr.consume("queue")
    except Exception:
        pass

    # Good
    from wredis._exceptions import QueueError, ValidationError

    try:
        mgr.consume("queue")
    except ValidationError:
        # Fix the input
        pass
    except QueueError:
        # Retry or alert
        pass

Pitfall 2: Forgetting to Close Connections
==========================================

If you do not use context managers, you **must** call ``close()`` (sync) or
``await close()`` (async) to release the connection pool.

.. code-block:: python

    # Sync
    mgr = RedisHashManager()
    try:
        mgr.set_json("key", value)
    finally:
        mgr.close()

    # Async
    mgr = AsyncRedisHashManager()
    try:
        await mgr.set_json("key", value)
    finally:
        await mgr.close()

Pitfall 3: Assuming Old Method Signatures
==========================================

The async API now uses ``redis.asyncio``. Methods that previously accepted
synchronous callbacks or returned synchronous iterators may now require
``await``. Always check the API documentation for the async variant of the
manager you are using.

Pitfall 4: Mixing Sync and Async Managers on the Same Pool
===========================================================

Do not share a ``ConnectionPool`` between sync and async managers. They use
different underlying drivers (``redis`` vs ``redis.asyncio``) and are not
compatible.

Pitfall 5: Cache Decorator Key Collisions
==========================================

The default key builder uses MD5 hashing of the function module, name, and
arguments. If two functions have the same name and signature in different
modules, they will produce different keys. However, if you use a custom
``key_builder``, ensure it produces unique keys across your application.

Use the ``prefix`` parameter to namespace caches::

    @cache(ttl=300, prefix="service_a")
    def get_user(user_id): ...

    @cache(ttl=300, prefix="service_b")
    def get_user(user_id): ...

Pitfall 6: Sentinel/Cluster Not a Drop-In Replacement
======================================================

``SentinelRedisManager`` and ``ClusterRedisManager`` have different
constructor signatures than the standard managers. They do not inherit from
``BaseManager``.

.. code-block:: python

    # Standard manager
    mgr = RedisHashManager(host="localhost", port=6379)

    # Sentinel manager (different signature)
    sentinel = SentinelRedisManager(
        sentinel_nodes=[("sentinel-1", 26379)],
        service_name="mymaster",
    )
    # Use sentinel.redis_client for Redis operations

    # Cluster manager (different signature)
    cluster = ClusterRedisManager(
        startup_nodes=[("node-1", 7000)],
    )
    # Use cluster.cluster for Redis operations

Pitfall 7: TTL Validation Is Now Strict
=========================================

In v0.x, a TTL of ``0`` might have been silently accepted or ignored. In
v1.0.0, ``validate_ttl()`` raises ``ValidationError`` for any TTL less than
``-1``. Use ``-1`` for no expiry or any positive integer for a TTL in
seconds.

.. code-block:: python

    from wredis._validation import validate_ttl
    from wredis._exceptions import ValidationError

    validate_ttl(-1)   # OK - no expiry
    validate_ttl(300)  # OK - 5 minutes
    validate_ttl(0)    # Raises ValidationError

==================
Quick Reference
==================

.. list-table:: v0.x to v1.0.0 Mapping
   :header-rows: 1
   :widths: 30 35 35

   * - Concept
     - v0.x
     - v1.0.0
   * - Error handling
     - ``logger.error``, return ``None``
     - Raise ``OperationError``, ``ValidationError``, etc.
   * - Async runtime
     - ``ThreadPoolExecutor``
     - ``redis.asyncio`` / ``asyncio`` tasks
   * - Connection
     - Implicit per-manager
     - Explicit ``ConnectionPool`` via ``BaseManager``
   * - Context manager
     - Not available
     - ``with`` / ``async with``
   * - Health check
     - Not available
     - ``health_check()`` method
   * - Geo operations
     - Not available
     - ``RedisGeoManager`` / ``AsyncRedisGeoManager``
   * - HyperLogLog
     - Not available
     - ``RedisHyperLogLogManager`` / ``AsyncRedisHyperLogLogManager``
   * - Pipeline
     - Not available
     - ``AsyncRedisPipelineManager``
   * - Transactions
     - Not available
     - ``AsyncRedisTransactionManager``
   * - Cache decorator
     - Not available
     - ``@cache``, ``@async_cache`` with ``CacheMetrics``
   * - Sentinel
     - Not available
     - ``SentinelRedisManager``
   * - Cluster
     - Not available
     - ``ClusterRedisManager``
   * - Retry
     - Not available
     - ``@retry``, ``@async_retry`` decorators
   * - Serialization
     - Manual ``json.dumps``/``loads``
     - ``wredis._serializer`` module
   * - Validation
     - Manual checks
     - ``wredis._validation`` module

==================
Need Help?
==================

- **Documentation:** https://wredis.readthedocs.io
- **Issue tracker:** https://github.com/anomalyco/wredis/issues
- **Changelog:** https://wredis.readthedocs.io/en/latest/changelog.html
