"""Unit tests for AsyncRedisHyperLogLogManager."""

import pytest

from wredis.async_api import AsyncRedisHyperLogLogManager


class TestAsyncRedisHyperLogLogManager:
    """Tests for AsyncRedisHyperLogLogManager."""

    @pytest.mark.asyncio
    async def test_add(self, async_redis_client):
        """Test adding elements to HyperLogLog."""
        manager = AsyncRedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        await manager.add("visitors", "user1", "user2", "user3")

        count = await async_redis_client.pfcount("visitors")
        assert count == 3

    @pytest.mark.asyncio
    async def test_count(self, async_redis_client):
        """Test counting unique elements."""
        manager = AsyncRedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        await manager.add("visitors", "user1", "user2", "user3")
        await manager.add("visitors", "user4", "user5")

        count = await manager.count("visitors")
        assert count == 5

    @pytest.mark.asyncio
    async def test_merge(self, async_redis_client):
        """Test merging HyperLogLogs."""
        manager = AsyncRedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        await manager.add("day1", "user1", "user2", "user3")
        await manager.add("day2", "user3", "user4", "user5")

        await manager.merge("total", "day1", "day2")

        count = await async_redis_client.pfcount("total")
        assert count == 5
