Cache Decorators
================

WRedis provides powerful cache decorators that implement the Cache-Aside pattern, allowing you to cache function results with minimal code changes.

Basic Caching
-------------

The ``@cache`` decorator caches function results in Redis. On subsequent calls with the same arguments, it returns the cached value instead of executing the function.

.. code-block:: python

   from wredis.decorators import cache

   @cache(ttl=300, prefix="api:users")
   def get_user_profile(user_id: int) -> dict:
       """Fetch user profile from database."""
       # Expensive database query
       return {"id": user_id, "name": "Alice", "role": "admin"}

   # First call - executes function, caches result
   user = get_user_profile(1001)

   # Second call - returns cached result (5 min TTL)
   user = get_user_profile(1001)

Parameters
~~~~~~~~~~

- ``ttl``: Time-to-live in seconds (default: 300)
- ``prefix``: Key prefix for cache entries (default: "wredis:cache")
- ``key_builder``: Custom function to generate cache keys
- ``redis_client``: Custom Redis client instance

Async Caching
-------------

Use ``@async_cache`` for async functions:

.. code-block:: python

   import asyncio
   from wredis.decorators import async_cache

   @async_cache(ttl=600, prefix="api:products")
   async def get_product(product_id: int) -> dict:
       """Fetch product from database asynchronously."""
       await asyncio.sleep(0.1)  # Simulate async DB query
       return {"id": product_id, "name": "Widget", "price": 9.99}

   async def main():
       product = await get_product(42)
       print(product)

   asyncio.run(main())

Cache Invalidation
------------------

Use ``@invalidate_cache`` to automatically clear cache after mutations:

.. code-block:: python

   from wredis.decorators import cache, invalidate_cache

   @cache(ttl=300, prefix="api:users")
   def get_user(user_id: int) -> dict:
       return {"id": user_id, "name": "Alice"}

   @invalidate_cache(pattern="api:users:*")
   def update_user(user_id: int, data: dict) -> dict:
       """Update user and invalidate cache."""
       # Update database
       return {"id": user_id, **data}

   # This will clear all keys matching "api:users:*"
   update_user(1001, {"name": "Alice Updated"})

Manual Cache Clearing
---------------------

Clear cache programmatically:

.. code-block:: python

   from wredis.decorators import clear_cache

   # Clear all user cache entries
   cleared = clear_cache(pattern="api:users:*")
   print(f"Cleared {cleared} cache entries")

Custom Key Builder
------------------

Override the default key generation:

.. code-block:: python

   from wredis.decorators import cache

   def custom_key_builder(func, args, kwargs):
       """Build cache key from function and arguments."""
       return f"{func.__name__}:{args[0]}"

   @cache(ttl=300, key_builder=custom_key_builder)
   def get_user(user_id: int) -> dict:
       return {"id": user_id, "name": "Alice"}

Best Practices
--------------

1. **Set appropriate TTLs** - Balance freshness vs. performance
2. **Use meaningful prefixes** - Organize cache by domain (e.g., ``api:users``, ``api:products``)
3. **Invalidate on mutations** - Always invalidate cache after data changes
4. **Monitor cache hit rates** - Track effectiveness of caching strategy
5. **Avoid caching sensitive data** - Be mindful of security implications
