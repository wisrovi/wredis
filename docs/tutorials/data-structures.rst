Data Structures
===============

WRedis provides managers for all major Redis data structures. This tutorial covers each structure with practical examples.

Bitmap
------

Bitmaps are ideal for tracking binary states like daily active users or feature flags.

.. code-block:: python

   from wredis.bitmap import RedisBitmapManager

   manager = RedisBitmapManager()

   # Track daily active users (user ID as offset)
   manager.set_bit("dau:2026-04-01", 1001, 1)
   manager.set_bit("dau:2026-04-01", 1002, 1)
   manager.set_bit("dau:2026-04-01", 1003, 1)

   # Count active users
   active_count = manager.count_bits("dau:2026-04-01")
   print(f"Active users: {active_count}")

   # Check if specific user was active
   is_active = manager.get_bit("dau:2026-04-01", 1001)
   print(f"User 1001 active: {bool(is_active)}")

Hash
----

Hashes are perfect for storing objects with multiple fields.

.. code-block:: python

   from wredis.hash import RedisHashManager

   manager = RedisHashManager()

   # Store user profile
   manager.create_hash("user:1001", "profile", {
       "name": "Alice",
       "email": "alice@example.com",
       "role": "admin"
   })

   # Read specific field
   profile = manager.read_hash("user:1001", "profile")
   print(profile)

   # Update existing field
   manager.update_hash("user:1001", "profile", {"role": "superadmin"})

   # Read all fields
   all_data = manager.read_all_hash("user:1001")

   # Delete specific field
   manager.delete_hash_field("user:1001", "profile")

Set
---

Sets are ideal for unique collections and membership testing.

.. code-block:: python

   from wredis.sets import RedisSetManager

   manager = RedisSetManager()

   # Add tags to a post
   manager.add_to_set("post:1001:tags", "python", "redis", "tutorial")

   # Check membership
   is_python = manager.is_member("post:1001:tags", "python")
   print(f"Has python tag: {is_python}")

   # Get all tags
   tags = manager.get_set_members("post:1001:tags")
   print(f"Tags: {tags}")

   # Remove a tag
   manager.remove_from_set("post:1001:tags", "tutorial")

Sorted Set
----------

Sorted sets maintain elements ordered by score, perfect for leaderboards.

.. code-block:: python

   from wredis.sortedset import RedisSortedSetManager

   manager = RedisSortedSetManager()

   # Add players with scores
   manager.add_to_sorted_set("leaderboard", 100, "player1")
   manager.add_to_sorted_set("leaderboard", 85, "player2")
   manager.add_to_sorted_set("leaderboard", 92, "player3")

   # Get top 3 players
   top_players = manager.get_sorted_set_reverse("leaderboard", stop=2)
   print(f"Top players: {top_players}")

   # Get player rank
   rank = manager.get_rank("leaderboard", "player2")
   print(f"Player2 rank: {rank}")

   # Increment score
   manager.increment_score("leaderboard", 10, "player2")

   # Get players by score range
   high_scorers = manager.get_sorted_set_by_score("leaderboard", 90, 100)
   print(f"High scorers: {high_scorers}")

HyperLogLog
-----------

HyperLogLog provides efficient cardinality estimation with minimal memory.

.. code-block:: python

   from wredis.hyperloglog import RedisHyperLogLogManager

   manager = RedisHyperLogLogManager()

   # Track daily unique visitors
   manager.add("visitors:2026-04-01", "user1", "user2", "user3")
   manager.add("visitors:2026-04-02", "user2", "user3", "user4")

   # Count unique visitors for a single day
   daily_count = manager.count("visitors:2026-04-01")
   print(f"Daily visitors: {daily_count}")

   # Merge and count across multiple days
   manager.merge("visitors:week1", "visitors:2026-04-01", "visitors:2026-04-02")
   weekly_count = manager.count("visitors:week1")
   print(f"Weekly visitors: {weekly_count}")

Geo
---

Geo operations enable location-based queries.

.. code-block:: python

   from wredis.geo import RedisGeoManager

   manager = RedisGeoManager()

   # Add store locations
   manager.add_location("stores", "sf_downtown", -122.4194, 37.7749)
   manager.add_location("stores", "sf_mission", -122.4084, 37.7849)
   manager.add_location("stores", "oakland", -122.2711, 37.8044)

   # Find stores within 5km
   nearby = manager.search_nearby("stores", -122.4194, 37.7749, 5, unit="km")
   print(f"Nearby stores: {nearby}")

   # Get distance between two stores
   distance = manager.get_distance("stores", "sf_downtown", "sf_mission", unit="km")
   print(f"Distance: {distance} km")

Pipeline
--------

Pipelines batch multiple commands for improved performance.

.. code-block:: python

   from wredis.pipeline import RedisPipelineManager

   manager = RedisPipelineManager()

   # Execute multiple commands in one round-trip
   results = manager.execute_commands([
       ("set", ["user:1:name", "Alice"]),
       ("set", ["user:1:email", "alice@example.com"]),
       ("set", ["user:1:role", "admin"]),
       ("get", ["user:1:name"]),
   ])

   # Set and get in one operation
   value = manager.set_get("temp:key", "temp_value")
   print(f"Set and got: {value}")

   # Batch set multiple keys
   manager.mset_pipeline({
       "key1": "value1",
       "key2": "value2",
       "key3": "value3",
   })

   # Batch get multiple keys
   values = manager.mget_pipeline("key1", "key2", "key3")

   # Delete multiple keys
   deleted = manager.delete_keys("key1", "key2", "key3")

Transaction
-----------

Transactions ensure atomic operations for data consistency.

.. code-block:: python

   from wredis.transaction import RedisTransactionManager

   manager = RedisTransactionManager()

   # Execute multiple commands atomically
   results = manager.execute_transaction([
       ("set", ["account:A", "1000"]),
       ("set", ["account:B", "500"]),
   ])

   # Atomic increment
   manager.increment_atomic("counter", 1)

   # Set if not exists (distributed lock)
   acquired = manager.set_if_not_exists("lock:resource", "locked", ttl=30)
   if acquired:
       # Perform critical section
       pass

   # Atomic get and set
   old_value = manager.get_and_set("config:version", "2.0")
   print(f"Previous version: {old_value}")

TTL Management
--------------

All managers support TTL operations for automatic key expiration.

.. code-block:: python

   # Set TTL during creation
   manager.create_hash("session:user1", "data", {"token": "abc"}, ttl=3600)

   # Check remaining TTL
   remaining = manager.get_ttl("session:user1")
   print(f"Remaining TTL: {remaining} seconds")

   # Extend TTL
   manager.extend_ttl("session:user1", 7200)

   # Keys with no TTL return -1
   # Non-existent keys return -2
