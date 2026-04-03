Exceptions Examples
===================

Examples demonstrating error handling and exception management for Redis operations.

.. code-block:: python

   from wredis import WRedis
   from wredis.exceptions import WRedisError

   try:
       client = WRedis()
       client.set("key", "value")
   except WRedisError as e:
       print(f"Redis error: {e}")

Examples
--------

.. list-table::
   :header-rows: 1

   * - Example
     - Description
   * - `01 Base Exception <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/01_base_exception.py>`_
     - Working with the base exception class
   * - `02 Exception Hierarchy <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/02_exception_hierarchy.py>`_
     - Understanding the exception hierarchy
   * - `03 Catching Specific Errors <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/03_catching_specific_errors.py>`_
     - Catching specific error types
   * - `04 Catch All WRedis Errors <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/04_catch_all_wredis_errors.py>`_
     - Catching all wredis errors
   * - `05 Custom Error Messages <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/05_custom_error_messages.py>`_
     - Customizing error messages
   * - `06 Validation Error Handling <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/06_validation_error_handling.py>`_
     - Handling validation errors
   * - `07 Operation Error Recovery <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/07_operation_error_recovery.py>`_
     - Recovering from operation errors
   * - `08 Transaction Error Handling <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/08_transaction_error_handling.py>`_
     - Error handling in transactions
   * - `09 Serialization Error Handling <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/09_serialization_error_handling.py>`_
     - Handling serialization errors
   * - `10 Logging Integration <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/10_logging_integration.py>`_
     - Integrating exceptions with logging
   * - `11 Retry on Specific Errors <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/11_retry_on_specific_errors.py>`_
     - Retrying on specific error types
   * - `12 Graceful Degradation <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/12_graceful_degradation.py>`_
     - Graceful degradation patterns
   * - `13 Queue Error Handling <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/13_queue_error_handling.py>`_
     - Error handling for queue operations
   * - `14 Stream and PubSub Errors <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/14_stream_and_pubsub_errors.py>`_
     - Handling stream and pub/sub errors
   * - `15 Custom Error Handler <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions/15_custom_error_handler.py>`_
     - Implementing custom error handlers

See `all examples on GitHub <https://github.com/wisrovi/wredis/tree/main/examples/sync/exceptions>`_.
