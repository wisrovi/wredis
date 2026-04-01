"""Unit tests for AsyncRedisPipelineManager."""

import pytest

from wredis.async_api import AsyncRedisPipelineManager


class TestAsyncRedisPipelineManager:
    """Tests for AsyncRedisPipelineManager."""

    @pytest.mark.asyncio
    async def test_execute_commands(self, async_redis_client):
        """Test executing multiple commands in pipeline."""
        manager = AsyncRedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        results = await manager.execute_commands(
            [
                ("set", ["key1", "value1"]),
                ("set", ["key2", "value2"]),
                ("get", ["key1"]),
            ]
        )

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_set_get(self, async_redis_client):
        """Test set and get in pipeline."""
        manager = AsyncRedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        result = await manager.set_get("mykey", "myvalue")

        assert result == "myvalue"

    @pytest.mark.asyncio
    async def test_mget_pipeline(self, async_redis_client):
        """Test mget in pipeline."""
        manager = AsyncRedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        await async_redis_client.set("key1", "value1")
        await async_redis_client.set("key2", "value2")

        results = await manager.mget_pipeline("key1", "key2")

        assert results[0] == "value1"
        assert results[1] == "value2"

    @pytest.mark.asyncio
    async def test_mset_pipeline(self, async_redis_client):
        """Test mset in pipeline."""
        manager = AsyncRedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        mapping = {"key1": "value1", "key2": "value2"}
        result = await manager.mset_pipeline(mapping)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_keys(self, async_redis_client):
        """Test deleting multiple keys in pipeline."""
        manager = AsyncRedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        await async_redis_client.set("key1", "value1")
        await async_redis_client.set("key2", "value2")

        deleted = await manager.delete_keys("key1", "key2")

        assert deleted == 2
