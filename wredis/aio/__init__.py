"""wredis.aio - Asynchronous Redis managers made simple.

This module provides a clean, unified API for all asynchronous Redis operations.
All managers handle connection pooling, retry logic, and error handling automatically.

Quick Start:
    from wredis.aio import BaseManager, RedisHashManager, cache

    # Simple async manager
    manager = BaseManager()
    await manager._execute("set", "key", "value")

    # With cache decorator
    @cache(ttl=60)
    async def get_user(user_id):
        return await fetch_from_db(user_id)

Available:
    - BaseManager: Low-level async with connection pooling and retry
    - RedisHashManager: Hash operations
    - RedisBitmapManager: Bitmap operations
    - RedisSetManager: Set operations
    - RedisSortedSetManager: Sorted set operations
    - RedisQueueManager: Queue operations
    - RedisPubSubManager: Pub/Sub operations
    - RedisStreamManager: Stream operations
    - RedisGeoManager: Geographic operations
    - RedisHyperLogLogManager: HyperLogLog operations
    - RedisPipelineManager: Pipeline operations
    - RedisTransactionManager: Transaction operations
    - CacheMetrics: Metrics tracking for cache
    - cache: Cache decorator
"""

from __future__ import annotations

from wredis._async_base import AsyncBaseManager as BaseManager
from wredis.async_api.bitmap import AsyncRedisBitmapManager as RedisBitmapManager
from wredis.async_api.geo import AsyncRedisGeoManager as RedisGeoManager
from wredis.async_api.hash import AsyncRedisHashManager as RedisHashManager
from wredis.async_api.hyperloglog import AsyncRedisHyperLogLogManager as RedisHyperLogLogManager
from wredis.async_api.pipeline import AsyncRedisPipelineManager as RedisPipelineManager
from wredis.async_api.pubsub import AsyncRedisPubSubManager as RedisPubSubManager
from wredis.async_api.queue import AsyncRedisQueueManager as RedisQueueManager
from wredis.async_api.sets import AsyncRedisSetManager as RedisSetManager
from wredis.async_api.sortedset import AsyncRedisSortedSetManager as RedisSortedSetManager
from wredis.async_api.streams import AsyncRedisStreamManager as RedisStreamManager
from wredis.async_api.transaction import AsyncRedisTransactionManager as RedisTransactionManager
from wredis.decorators import CacheMetrics, async_cache as cache

__all__ = [
    "BaseManager",
    "CacheMetrics",
    "RedisBitmapManager",
    "RedisGeoManager",
    "RedisHashManager",
    "RedisHyperLogLogManager",
    "RedisPipelineManager",
    "RedisPubSubManager",
    "RedisQueueManager",
    "RedisSetManager",
    "RedisSortedSetManager",
    "RedisStreamManager",
    "RedisTransactionManager",
    "cache",
]
