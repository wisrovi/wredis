"""Async Redis managers for WRedis."""

from __future__ import annotations

from wredis.async_api.bitmap import AsyncRedisBitmapManager
from wredis.async_api.geo import AsyncRedisGeoManager
from wredis.async_api.hash import AsyncRedisHashManager
from wredis.async_api.hyperloglog import AsyncRedisHyperLogLogManager
from wredis.async_api.pipeline import AsyncRedisPipelineManager
from wredis.async_api.pubsub import AsyncRedisPubSubManager
from wredis.async_api.queue import AsyncRedisQueueManager
from wredis.async_api.sets import AsyncRedisSetManager
from wredis.async_api.sortedset import AsyncRedisSortedSetManager
from wredis.async_api.streams import AsyncRedisStreamManager
from wredis.async_api.transaction import AsyncRedisTransactionManager

__all__ = [
    "AsyncRedisBitmapManager",
    "AsyncRedisGeoManager",
    "AsyncRedisHashManager",
    "AsyncRedisHyperLogLogManager",
    "AsyncRedisPipelineManager",
    "AsyncRedisPubSubManager",
    "AsyncRedisQueueManager",
    "AsyncRedisSetManager",
    "AsyncRedisSortedSetManager",
    "AsyncRedisStreamManager",
    "AsyncRedisTransactionManager",
]
