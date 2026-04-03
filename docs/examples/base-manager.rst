Base Manager Examples
=====================

Examples demonstrating the base Redis manager for connection handling and operations.

.. code-block:: python

   from wredis import WRedis

   client = WRedis(host="localhost", port=6379, db=0)
   client.set("key", "value")
   value = client.get("key")

Examples
--------

.. list-table::
   :header-rows: 1

   * - Example
     - Description
   * - `01 Basic Init <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/01_basic_init.py>`_
     - Basic client initialization
   * - `02 Custom Config <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/02_custom_config.py>`_
     - Custom configuration options
   * - `03 Health Check <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/03_health_check.py>`_
     - Performing health checks
   * - `04 Context Manager <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/04_context_manager.py>`_
     - Using context manager for connections
   * - `05 Execute with Retry <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/05_execute_with_retry.py>`_
     - Executing operations with retry logic
   * - `06 Logging <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/06_logging.py>`_
     - Integrating logging with the manager
   * - `07 Connection Pooling <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/07_connection_pooling.py>`_
     - Configuring connection pools
   * - `08 Error Handling <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/08_error_handling.py>`_
     - Error handling patterns
   * - `09 Custom Manager <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/09_custom_manager.py>`_
     - Creating custom manager subclasses
   * - `10 Multiple Instances <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/10_multiple_instances.py>`_
     - Managing multiple Redis instances
   * - `11 Batch Operations <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/11_batch_operations.py>`_
     - Performing batch operations
   * - `12 Verbose Mode <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/12_verbose_mode.py>`_
     - Enabling verbose output
   * - `13 Unit Testing <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/13_unit_testing.py>`_
     - Unit testing with the manager
   * - `14 Pipeline Operations <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/14_pipeline_operations.py>`_
     - Using Redis pipelines
   * - `15 Connection Pool Monitoring <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager/15_connection_pool_monitoring.py>`_
     - Monitoring connection pool status

See `all examples on GitHub <https://github.com/wisrovi/wredis/tree/main/examples/sync/base_manager>`_.
