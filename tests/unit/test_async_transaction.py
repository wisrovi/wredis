"""Unit tests for AsyncRedisTransactionManager."""

import pytest

from wredis.async_api import AsyncRedisTransactionManager


class TestAsyncRedisTransactionManager:
    """Tests for AsyncRedisTransactionManager."""

    @pytest.mark.asyncio
    async def test_execute_transaction(self, async_redis_client):
        """Test executing multiple commands in transaction."""
        manager = AsyncRedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        results = await manager.execute_transaction(
            [
                ("set", ["balance:alice", "100"]),
                ("incrby", ["balance:alice", 50]),
                ("get", ["balance:alice"]),
            ]
        )

        assert results[0] is True
        assert results[1] == 150

    @pytest.mark.asyncio
    async def test_set_if_not_exists(self, async_redis_client):
        """Test SET NX (set if not exists)."""
        manager = AsyncRedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        result1 = await manager.set_if_not_exists("lock", "locked", ttl=60)
        assert result1 is True

        result2 = await manager.set_if_not_exists("lock", "locked_again", ttl=60)
        assert result2 is False

    @pytest.mark.asyncio
    async def test_increment_atomic(self, async_redis_client):
        """Test atomic increment."""
        manager = AsyncRedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        await async_redis_client.set("counter", "10")

        result1 = await manager.increment_atomic("counter", 5)
        assert result1 == 15

    @pytest.mark.asyncio
    async def test_get_and_set(self, async_redis_client):
        """Test atomic get and set."""
        manager = AsyncRedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        await async_redis_client.set("mykey", "old_value")

        old = await manager.get_and_set("mykey", "new_value")

        assert old == "old_value"
