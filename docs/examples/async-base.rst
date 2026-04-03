Async Base Examples
===================

Examples demonstrating async Redis operations and connection management.

.. code-block:: python

   from wredis import AsyncWRedis

   async with AsyncWRedis() as client:
       await client.set("key", "value")
       value = await client.get("key")

Examples
--------

.. list-table::
   :header-rows: 1

   * - Example
     - Description
   * - `01 Basic Init <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/01_basic_init.py>`_
     - Basic async client initialization
   * - `02 Health Check <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/02_health_check.py>`_
     - Async health check operations
   * - `03 Async Context Manager <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/03_async_context_manager.py>`_
     - Using async context managers
   * - `04 Execute with Retry <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/04_execute_with_retry.py>`_
     - Async retry execution
   * - `05 FastAPI Integration <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/05_fastapi_integration.py>`_
     - Integrating with FastAPI
   * - `06 Concurrent Operations <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/06_concurrent_operations.py>`_
     - Running concurrent async operations
   * - `07 Connection Pooling <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/07_connection_pooling.py>`_
     - Async connection pool configuration
   * - `08 Error Handling <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/08_error_handling.py>`_
     - Async error handling patterns
   * - `09 Custom Async Manager <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/09_custom_async_manager.py>`_
     - Creating custom async managers
   * - `10 Logging Integration <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/10_logging_integration.py>`_
     - Logging in async operations
   * - `11 Multiple Databases <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/11_multiple_databases.py>`_
     - Managing multiple async database connections
   * - `12 Async Worker Pattern <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/12_async_worker_pattern.py>`_
     - Async worker pattern implementation
   * - `13 Async Cache Decorator <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/13_async_cache_decorator.py>`_
     - Async caching with decorators
   * - `14 Rate Limiter <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/14_rate_limiter.py>`_
     - Async rate limiting with Redis
   * - `15 FastAPI Advanced <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base/15_fastapi_advanced.py>`_
     - Advanced FastAPI integration patterns

See `all examples on GitHub <https://github.com/wisrovi/wredis/tree/main/examples/async/async_base>`_.
