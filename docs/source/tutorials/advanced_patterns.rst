Advanced Design Patterns
========================

This guide explores advanced patterns and best practices for building scalable and resilient applications with WRedis.

Pipeline and Atomic Transactions
--------------------------------------------------------------------------------

When you need to execute multiple commands, using a Pipeline can significantly improve performance by reducing round-trip time.

.. code-block:: python

   from wredis.sync import RedisPipelineManager

   pipeline = RedisPipelineManager(host="localhost")
   
   # Queue multiple commands
   pipeline.set("key1", "value1")
   pipeline.set("key2", "value2")
   pipeline.hset("hash1", "field1", "data")
   
   # Execute all at once
   results = pipeline.execute()

For atomicity, use the ``RedisTransactionManager`` which implements ``WATCH/MULTI/EXEC``.

Custom Cache Key Generation
--------------------------------------------------------------------------------

The ``@cache`` decorator allows you to customize how keys are generated to avoid collisions or to implement complex caching logic.

.. code-block:: python

   from wredis import cache

   def custom_key(func_name, *args, **kwargs):
       return f"myapp:custom:{func_name}:{args[0]}"

   @cache(ttl=60, prefix="user", key_generator=custom_key)
   def get_user_data(user_id):
       # The key will be "myapp:custom:get_user_data:123"
       return fetch_from_db(user_id)

Performance Tuning: Connection Pools
--------------------------------------------------------------------------------

WRedis managers use connection pooling by default. You can tune the pool size for high-concurrency environments.

.. code-block:: python

   from wredis.sync import RedisHashManager

   # Configure max connections
   manager = RedisHashManager(
       host="localhost", 
       max_connections=50,
       socket_timeout=5
   )

Advanced Error Handling
--------------------------------------------------------------------------------

In production, always catch specific WRedis exceptions to implement fallback logic.

.. code-block:: python

   from wredis.sync import RedisQueueManager
   from wredis.exceptions import QueueError, OperationError

   qm = RedisQueueManager()

   try:
       qm.publish("notifications", {"msg": "hello"})
   except QueueError:
       # Handle queue-specific failures (e.g., full, invalid format)
       log_to_dead_letter_file()
   except OperationError:
       # Handle connection or Redis-level failures
       retry_later()
