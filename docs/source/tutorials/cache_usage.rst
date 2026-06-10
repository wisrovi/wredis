Cache Usage
================================================================================

The ``@cache`` decorator is one of the most powerful features of WRedis. It allows you to transparently cache function results in Redis.

Basic Usage
--------------------------------------------------------------------------------

.. code-block:: python

   from wredis import cache

   @cache(ttl=300, prefix="user_profile")
   def get_user_profile(user_id: int):
       # This result will be cached for 5 minutes
       return database.query_profile(user_id)

Cache Metrics
--------------------------------------------------------------------------------

WRedis automatically tracks cache performance metrics:

.. code-block:: python

   from wredis.sync import CacheMetrics

   metrics = CacheMetrics()
   print(f"Hit Rate: {metrics.hit_rate}%")
   print(f"Hits: {metrics.hits}")
   print(f"Misses: {metrics.misses}")

Advanced Configuration
--------------------------------------------------------------------------------

You can configure the host and port for the cache:

.. code-block:: python

   @cache(ttl=60, host="redis.internal", port=6379)
   def fetch_data():
       pass
