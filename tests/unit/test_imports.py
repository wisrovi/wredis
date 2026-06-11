"""Test that all __init__ modules and re-exports import correctly."""


class TestImports:
    """Test that all modules import correctly."""

    def test_sync_init(self):
        """Test wredis.sync.__init__ imports."""
        from wredis.sync import (
            BaseManager,
            CacheMetrics,
            RedisBitmapManager,
            RedisGeoManager,
            RedisHashManager,
            RedisHyperLogLogManager,
            RedisPipelineManager,
            RedisPubSubManager,
            RedisQueueManager,
            RedisSetManager,
            RedisSortedSetManager,
            RedisStreamManager,
            RedisTransactionManager,
            cache,
        )
        assert BaseManager is not None
        assert cache is not None
        assert CacheMetrics is not None

    def test_aio_init(self):
        """Test wredis.aio.__init__ imports."""
        from wredis.aio import (
            BaseManager,
            CacheMetrics,
            RedisBitmapManager,
            RedisGeoManager,
            RedisHashManager,
            RedisHyperLogLogManager,
            RedisPipelineManager,
            RedisPubSubManager,
            RedisQueueManager,
            RedisSetManager,
            RedisSortedSetManager,
            RedisStreamManager,
            RedisTransactionManager,
            cache,
        )
        assert BaseManager is not None
        assert cache is not None
        assert CacheMetrics is not None

    def test_exceptions_module(self):
        """Test wredis.exceptions re-exports."""
        from wredis.exceptions import (
            OperationError,
            PubSubError,
            QueueError,
            StreamError,
            TransactionError,
            ValidationError,
            WRedisError,
        )
        assert OperationError is not None
        assert PubSubError is not None
        assert QueueError is not None
        assert StreamError is not None
        assert TransactionError is not None
        assert ValidationError is not None
        assert WRedisError is not None

    def test_async_api_init(self):
        """Test wredis.async_api.__init__ imports."""
        from wredis.async_api import (
            AsyncRedisBitmapManager,
            AsyncRedisGeoManager,
            AsyncRedisHashManager,
            AsyncRedisHyperLogLogManager,
            AsyncRedisPipelineManager,
            AsyncRedisPubSubManager,
            AsyncRedisQueueManager,
            AsyncRedisSetManager,
            AsyncRedisSortedSetManager,
            AsyncRedisStreamManager,
            AsyncRedisTransactionManager,
        )
        assert AsyncRedisBitmapManager is not None

    def test_ha_init(self):
        """Test wredis.ha.__init__ imports."""
        from wredis.ha import ClusterRedisManager, SentinelRedisManager
        assert ClusterRedisManager is not None
        assert SentinelRedisManager is not None
