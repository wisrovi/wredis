"""wredis.sync - Synchronous Redis managers made simple.

This module provides a clean, unified API for all synchronous Redis operations.
All managers handle connection pooling, retry logic, and error handling automatically.

Quick Start:
    from wredis.sync import BaseManager, RedisHashManager, cache

    # Simple manager
    manager = BaseManager()
    manager.set("key", "value")

    # With cache decorator
    @cache(ttl=60)
    def get_user(user_id):
        return fetch_from_db(user_id)

Available:
    - BaseManager: Low-level with connection pooling and retry
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

from wredis._base import BaseManager
from wredis.bitmap import RedisBitmapManager
from wredis.decorators import CacheMetrics, cache
from wredis.geo import RedisGeoManager
from wredis.hash import RedisHashManager
from wredis.hyperloglog import RedisHyperLogLogManager
from wredis.pipeline import RedisPipelineManager
from wredis.pubsub import RedisPubSubManager
from wredis.queue import RedisQueueManager
from wredis.sets import RedisSetManager
from wredis.sortedset import RedisSortedSetManager
from wredis.streams import RedisStreamManager
from wredis.transaction import RedisTransactionManager

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
