API Stability Guarantee
=======================

WRedis commits to maintaining a stable public API within each major version.
This document defines what constitutes the public API, the deprecation process,
and the compatibility guarantees for users of the library.

Public API Definition
---------------------

The public API of WRedis consists of all symbols that are:

1. Exported in ``wredis/__init__.py`` via ``__all__``
2. Exported in ``wredis/async_api/__init__.py`` via ``__all__``
3. Exported in subpackage ``__init__.py`` files (e.g., ``wredis.bitmap.__init__.py``)
4. Decorators in ``wredis.decorators``
5. Exception classes in ``wredis._exceptions`` (imported via ``wredis.exceptions``)

Anything NOT listed above is considered **private** and may change at any time
without notice or deprecation warning.

What is Private
---------------

The following are considered private implementation details:

- Any module, class, function, or variable prefixed with an underscore (``_``)
  (e.g., ``wredis._base``, ``wredis._serializer``, ``wredis._validation``)
- Any module inside a ``_``-prefixed package (e.g., ``wredis._modules.*``)
- Internal methods of public classes (methods starting with ``_``)
- The ``wredis._connection`` module
- The ``wredis._types`` module
- The ``wredis._retry`` module
- The ``wredis._async_base`` module
- Any attribute not documented in the public API section below

Stability Guarantee
-------------------

Within a major version (e.g., 1.x.x):

- **Public classes** will not be removed or renamed
- **Public method signatures** will not have required parameters added
- **Public function signatures** will not have required parameters added
- **Exception classes** will not be removed or have their inheritance changed
- **Decorator signatures** will not have required parameters added
- **Return types** will not change in a breaking way

Breaking changes (signature changes, removals, behavioral changes) will only
occur in a new major version (e.g., 2.0.0).

Deprecation Process
-------------------

When a public API element needs to be removed or significantly changed:

1. **Version N**: The element is marked as deprecated using
   ``warnings.warn(..., DeprecationWarning)``. Documentation is updated to
   indicate the deprecation and the recommended alternative.

2. **Version N+1**: The deprecation warning continues. The alternative API
   is fully functional and documented.

3. **Version N+2**: The deprecated element is removed.

This means a deprecated API will be available for at least **2 minor versions**
after the deprecation warning is first issued, giving users ample time to migrate.

Example deprecation pattern::

    import warnings

    def old_method():
        warnings.warn(
            "old_method() is deprecated and will be removed in wredis 1.4.0. "
            "Use new_method() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return _old_method_impl()

Public API
----------

Sync Managers
~~~~~~~~~~~~~

The following classes are available from the top-level ``wredis`` package:

=============================  ===================================
Class                          Source Module
=============================  ===================================
``RedisBitmapManager``         ``wredis.bitmap``
``RedisHashManager``           ``wredis.hash``
``RedisPubSubManager``         ``wredis.pubsub``
``RedisQueueManager``          ``wredis.queue``
``RedisSetManager``            ``wredis.sets``
``RedisSortedSetManager``      ``wredis.sortedset``
``RedisStreamManager``         ``wredis.streams``
``RedisPipelineManager``       ``wredis.pipeline``
``RedisTransactionManager``    ``wredis.transaction``
``RedisGeoManager``            ``wredis.geo``
``RedisHyperLogLogManager``    ``wredis.hyperloglog``
=============================  ===================================

Convenience Functions
~~~~~~~~~~~~~~~~~~~~~

The following functions are available from the top-level ``wredis`` package:

=============================  ===================================
Function                       Description
=============================  ===================================
``publish(channel, message)``  Publish a message to a Redis channel
``subscribe(channel, cb)``     Subscribe to a Redis channel
``enqueue(queue_name, data)``  Add a message to a Redis queue
``xadd(stream_name, data)``    Add a message to a Redis stream
=============================  ===================================

Async Managers
~~~~~~~~~~~~~~

The following classes are available from ``wredis.async_api``:

==================================  ===================================
Class                               Source Module
==================================  ===================================
``AsyncRedisBitmapManager``         ``wredis.async_api.bitmap``
``AsyncRedisHashManager``           ``wredis.async_api.hash``
``AsyncRedisPubSubManager``         ``wredis.async_api.pubsub``
``AsyncRedisQueueManager``          ``wredis.async_api.queue``
``AsyncRedisSetManager``            ``wredis.async_api.sets``
``AsyncRedisSortedSetManager``      ``wredis.async_api.sortedset``
``AsyncRedisStreamManager``         ``wredis.async_api.streams``
``AsyncRedisPipelineManager``       ``wredis.async_api.pipeline``
``AsyncRedisTransactionManager``    ``wredis.async_api.transaction``
``AsyncRedisGeoManager``            ``wredis.async_api.geo``
``AsyncRedisHyperLogLogManager``    ``wredis.async_api.hyperloglog``
==================================  ===================================

Decorators
~~~~~~~~~~

The following decorators are available from ``wredis.decorators``:

=============================  ===================================
Decorator                       Description
=============================  ===================================
``@cache``                      Cache function results in Redis
``@async_cache``                Async version of @cache
``@invalidate_cache``           Invalidate cache after execution
=============================  ===================================

Utility Classes
~~~~~~~~~~~~~~~

=============================  ===================================
Class                           Description
=============================  ===================================
``CacheMetrics``                Tracks cache hit/miss statistics
=============================  ===================================

Exceptions
~~~~~~~~~~

All exceptions inherit from ``WRedisError`` and are available from
``wredis._exceptions``:

=============================  ===================================
Exception                       Description
=============================  ===================================
``WRedisError``                 Base exception for all WRedis errors
``RedisConnectionError``        Connection to Redis failed
``SerializationError``          Serialization/deserialization failed
``CacheError``                  Cache operations failed
``SentinelError``               Sentinel operations failed
``ClusterError``                Cluster operations failed
``ValidationError``             Input validation failed
``OperationError``              A Redis operation failed
``TransactionError``            Transaction failed (e.g., WATCH conflict)
``QueueError``                  Queue operations failed
``StreamError``                 Stream operations failed
``PubSubError``                 Pub/sub operations failed
=============================  ===================================

High Availability
~~~~~~~~~~~~~~~~~

=============================  ===================================
Class                           Source Module
=============================  ===================================
``RedisSentinelManager``        ``wredis.ha.sentinel``
``RedisClusterManager``         ``wredis.ha.cluster``
=============================  ===================================

API Stability Status
--------------------

Stable API
~~~~~~~~~~

These elements are considered stable and will not change within the 1.x series:

- All sync managers listed above (full method stability)
- All async managers listed above (full method stability)
- All convenience functions (``publish``, ``subscribe``, ``enqueue``, ``xadd``)
- All decorators (``@cache``, ``@async_cache``, ``@invalidate_cache``)
- ``CacheMetrics`` class
- All exception classes
- ``clear_cache()`` utility function

Experimental API
~~~~~~~~~~~~~~~~

These elements are functional but may receive minor refinements (non-breaking):

- ``RedisClusterManager`` — cluster support is still maturing
- ``RedisSentinelManager`` — sentinel failover edge cases under review
- ``AsyncRedisTransactionManager`` — async transaction patterns evolving

Private API (No Stability Guarantee)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These modules are internal and may change without notice:

- ``wredis._base`` — base sync manager
- ``wredis._async_base`` — base async manager
- ``wredis._connection`` — connection utilities
- ``wredis._serializer`` — JSON serialization
- ``wredis._validation`` — input validation
- ``wredis._retry`` — retry logic
- ``wredis._types`` — type definitions
- ``wredis._exceptions`` — exception definitions

Version Compatibility Matrix
----------------------------

Python Compatibility
~~~~~~~~~~~~~~~~~~~~

============  =========  =========  =========  =========
WRedis        Python     Python     Python     Python
              3.10       3.11       3.12       3.13
============  =========  =========  =========  =========
1.0.x         Supported  Supported  Supported  Supported
============  =========  =========  =========  =========

Redis Compatibility
~~~~~~~~~~~~~~~~~~~

============  =========  =========  =========
WRedis        Redis 6    Redis 7    Redis 8
============  =========  =========  =========
1.0.x         Supported  Supported  Supported
============  =========  =========  =========

Dependency Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~

============  =========  =========
WRedis        redis-py   loguru
============  =========  =========
1.0.x         >= 5.0.0   >= 0.7.0
============  =========  =========

Reporting API Issues
--------------------

If you encounter a breaking change within a major version, please:

1. Open an issue at https://github.com/wisrovi/wredis/issues
2. Include the WRedis version, Python version, and Redis version
3. Provide a minimal reproduction case

Breaking changes within a major version are considered bugs and will be fixed.
