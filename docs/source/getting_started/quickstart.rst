Quickstart Guide
================================================================================

This guide will help you get started with WRedis in minutes.

Basic Synchronous Example
--------------------------------------------------------------------------------

Using ``RedisHashManager`` to store and retrieve data:

.. code-block:: python

   from wredis.sync import RedisHashManager

   # Initialize
   manager = RedisHashManager(host="localhost", port=6379)

   # Create a hash
   manager.create_hash("my_app:session:1", "user_id", "42", ttl=300)

   # Read data
   user_id = manager.read_hash("my_app:session:1", "user_id")
   print(f"User ID: {user_id}")

Basic Asynchronous Example
--------------------------------------------------------------------------------

Using ``AsyncRedisHashManager`` with ``asyncio``:

.. code-block:: python

   import asyncio
   from wredis.aio import AsyncRedisHashManager

   async def main():
       # Initialize
       manager = AsyncRedisHashManager(host="localhost")
       
       # Create hash
       await manager.create_hash("async_key", "field", {"data": 123})
       
       # Read hash
       result = await manager.read_hash("async_key", "field")
       print(f"Result: {result}")

   if __name__ == "__main__":
       asyncio.run(main())

Using the Cache Decorator
--------------------------------------------------------------------------------

WRedis provides a powerful cache decorator with built-in metrics:

.. code-block:: python

   from wredis import cache
   import time

   @cache(ttl=60, prefix="compute")
   def expensive_operation(x, y):
       time.sleep(2) # Simulate heavy work
       return x + y

   # First call: 2 seconds
   print(expensive_operation(10, 20))

   # Second call: instantaneous (from Redis)
   print(expensive_operation(10, 20))
