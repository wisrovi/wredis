Async Usage
===========

WRedis provides full async/await support for all managers, making it ideal for FastAPI, aiohttp, and other async frameworks.

Basic Async Pattern
-------------------

All async managers follow the same pattern as their sync counterparts, with ``await`` for all operations:

.. code-block:: python

   import asyncio
   from wredis.async_api.hash import AsyncRedisHashManager

   async def main():
       manager = AsyncRedisHashManager(host="localhost", port=6379, db=0)

       # Store data
       await manager.create_hash("user:1", "profile", {
           "name": "Alice",
           "email": "alice@example.com"
       })

       # Retrieve data
       profile = await manager.read_hash("user:1", "profile")
       print(profile)

   asyncio.run(main())

Async Hash Operations
---------------------

.. code-block:: python

   import asyncio
   from wredis.async_api.hash import AsyncRedisHashManager

   async def user_management():
       manager = AsyncRedisHashManager()

       # Create
       await manager.create_hash("user:100", "settings", {
           "theme": "dark",
           "notifications": True
       })

       # Read
       settings = await manager.read_hash("user:100", "settings")

       # Update
       await manager.update_hash("user:100", "settings", {"theme": "light"})

       # Read all
       all_data = await manager.read_all_hash("user:100")

       # Delete field
       await manager.delete_hash_field("user:100", "settings")

   asyncio.run(user_management())

Async Pub/Sub
-------------

.. code-block:: python

   import asyncio
   from wredis.async_api.pubsub import AsyncRedisPubSubManager

   async def pubsub_example():
       manager = AsyncRedisPubSubManager()

       # Publish
       await manager.publish_message("notifications", {
           "type": "email",
           "to": "user@example.com",
           "subject": "Welcome!"
       })

   asyncio.run(pubsub_example())

Async Pipeline
--------------

.. code-block:: python

   import asyncio
   from wredis.async_api.pipeline import AsyncRedisPipelineManager

   async def batch_operations():
       manager = AsyncRedisPipelineManager()

       results = await manager.execute_commands([
           ("set", ["key1", "value1"]),
           ("set", ["key2", "value2"]),
           ("get", ["key1"]),
       ])

       print(results)

   asyncio.run(batch_operations())

Async Sorted Sets
-----------------

.. code-block:: python

   import asyncio
   from wredis.async_api.sortedset import AsyncRedisSortedSetManager

   async def leaderboard():
       manager = AsyncRedisSortedSetManager()

       # Add scores
       await manager.add_to_sorted_set("leaderboard", 100, "player1")
       await manager.add_to_sorted_set("leaderboard", 85, "player2")
       await manager.add_to_sorted_set("leaderboard", 92, "player3")

       # Get top players
       top = await manager.get_sorted_set_reverse("leaderboard", stop=2)
       print(f"Top players: {top}")

       # Get rank
       rank = await manager.get_rank("leaderboard", "player2")
       print(f"Player2 rank: {rank}")

   asyncio.run(leaderboard())

Async Geo Operations
--------------------

.. code-block:: python

   import asyncio
   from wredis.async_api.geo import AsyncRedisGeoManager

   async def geo_example():
       manager = AsyncRedisGeoManager()

       # Add locations
       await manager.add_location("stores", "store_a", -122.4194, 37.7749)
       await manager.add_location("stores", "store_b", -122.4084, 37.7849)

       # Find nearby
       nearby = await manager.search_nearby("stores", -122.4194, 37.7749, 5, unit="km")
       print(f"Nearby stores: {nearby}")

       # Get distance
       distance = await manager.get_distance("stores", "store_a", "store_b", unit="km")
       print(f"Distance: {distance} km")

   asyncio.run(geo_example())

Async HyperLogLog
-----------------

.. code-block:: python

   import asyncio
   from wredis.async_api.hyperloglog import AsyncRedisHyperLogLogManager

   async def analytics():
       manager = AsyncRedisHyperLogLogManager()

       # Track unique visitors
       await manager.add("visitors:2026-04-01", "user1", "user2", "user3")
       await manager.add("visitors:2026-04-02", "user2", "user3", "user4")

       # Count unique visitors
       count = await manager.count("visitors:2026-04-01", "visitors:2026-04-02")
       print(f"Total unique visitors: {count}")

   asyncio.run(analytics())

FastAPI Integration
-------------------

Example with FastAPI:

.. code-block:: python

   from fastapi import FastAPI
   from wredis.async_api.hash import AsyncRedisHashManager
   from wredis.decorators import async_cache

   app = FastAPI()
   hash_manager = AsyncRedisHashManager()

   @async_cache(ttl=60, prefix="api:users")
   @app.get("/users/{user_id}")
   async def get_user(user_id: int):
       return await hash_manager.read_hash(f"user:{user_id}", "profile")

   @app.post("/users/{user_id}")
   async def create_user(user_id: int, profile: dict):
       await hash_manager.create_hash(f"user:{user_id}", "profile", profile)
       return {"status": "created"}

Performance Considerations
--------------------------

1. **Connection pooling** - Async managers use connection pooling by default
2. **Concurrent operations** - Use ``asyncio.gather()`` for parallel operations
3. **Pipeline batching** - Group related commands in pipelines for reduced latency
4. **Resource cleanup** - Managers handle cleanup automatically on exit
