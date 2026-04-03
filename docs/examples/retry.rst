Retry Examples
==============

Examples demonstrating retry logic for Redis operations with backoff strategies.

.. code-block:: python

   from wredis import WRedis

   client = WRedis(retry_attempts=3, retry_delay=1.0)
   # Operations automatically retry on failure
   value = client.get("my_key")

Examples
--------

.. list-table::
   :header-rows: 1

   * - Example
     - Description
   * - `01 Basic Retry <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/01_basic_retry.py>`_
     - Basic retry configuration
   * - `02 Custom Exceptions <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/02_custom_exceptions.py>`_
     - Retrying on custom exception types
   * - `03 Backoff Timing <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/03_backoff_timing.py>`_
     - Configuring backoff timing strategies
   * - `04 Redis Read Operations <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/04_redis_read_operations.py>`_
     - Retry patterns for read operations
   * - `05 Redis Write Operations <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/05_redis_write_operations.py>`_
     - Retry patterns for write operations
   * - `06 Database Connection <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/06_database_connection.py>`_
     - Retry on connection failures
   * - `07 API Calls <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/07_api_calls.py>`_
     - Retry patterns for API integrations
   * - `08 Circuit Breaker <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/08_circuit_breaker.py>`_
     - Circuit breaker pattern with retry
   * - `09 Retry with Logging <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/09_retry_with_logging.py>`_
     - Logging retry attempts
   * - `10 Retry with Wrapper <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/10_retry_with_wrapper.py>`_
     - Using retry wrapper functions
   * - `11 Batch Operations <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/11_batch_operations.py>`_
     - Retry for batch operations
   * - `12 Retry with Fallback <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/12_retry_with_fallback.py>`_
     - Fallback strategies on retry exhaustion
   * - `13 Retry with Timeout <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/13_retry_with_timeout.py>`_
     - Combining retry with timeout handling
   * - `14 Async Retry <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/14_async_retry.py>`_
     - Async retry patterns
   * - `15 Async Retry FastAPI <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry/15_async_retry_fastapi.py>`_
     - Async retry in FastAPI applications

See `all examples on GitHub <https://github.com/wisrovi/wredis/tree/main/examples/sync/retry>`_.
