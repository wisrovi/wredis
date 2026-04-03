"""Tests for AsyncRedisPipelineManager."""

from unittest.mock import AsyncMock, MagicMock, patch

import fakeredis.aioredis
import pytest

from wredis.async_api.pipeline import AsyncRedisPipelineManager


@pytest.fixture
async def async_client():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield fake
    await fake.aclose()


@pytest.fixture
def manager():
    return AsyncRedisPipelineManager(verbose=False)


class TestAsyncRedisPipelineManagerInit:
    """Tests for initialization."""

    def test_init_defaults(self):
        m = AsyncRedisPipelineManager()
        assert m.verbose is True

    def test_init_custom(self):
        m = AsyncRedisPipelineManager(host="myhost", port=1234, db=2, verbose=False)
        assert m.verbose is False


class TestAsyncRedisPipelineManagerExecuteCommands:
    """Tests for execute_commands method."""

    @pytest.mark.asyncio
    async def test_execute_multiple_commands(self, async_client, manager):
        manager.redis_client = async_client
        commands = [
            ("set", ["key1", "value1"]),
            ("set", ["key2", "value2"]),
            ("get", ["key1"]),
        ]
        results = await manager.execute_commands(commands)
        assert results[0] is True
        assert results[1] is True
        assert results[2] == "value1"

    @pytest.mark.asyncio
    async def test_execute_empty_commands(self, async_client, manager):
        manager.redis_client = async_client
        results = await manager.execute_commands([])
        assert results == []

    @pytest.mark.asyncio
    async def test_execute_hash_commands(self, async_client, manager):
        manager.redis_client = async_client
        commands = [
            ("hset", ["myhash", "field1", "value1"]),
            ("hget", ["myhash", "field1"]),
        ]
        results = await manager.execute_commands(commands)
        assert results[0] == 1
        assert results[1] == "value1"

    @pytest.mark.asyncio
    async def test_execute_list_commands(self, async_client, manager):
        manager.redis_client = async_client
        commands = [
            ("rpush", ["mylist", "a", "b"]),
            ("llen", ["mylist"]),
        ]
        results = await manager.execute_commands(commands)
        assert results[0] == 2
        assert results[1] == 2

    @pytest.mark.asyncio
    async def test_execute_error(self, manager):
        mock_client = MagicMock()
        mock_client.pipeline.side_effect = Exception("connection error")
        manager.redis_client = mock_client
        results = await manager.execute_commands([("set", ["k", "v"])])
        assert results == []


class TestAsyncRedisPipelineManagerSetGet:
    """Tests for set_get method."""

    @pytest.mark.asyncio
    async def test_set_get_basic(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.set_get("mykey", "myvalue")
        assert result == "myvalue"

    @pytest.mark.asyncio
    async def test_set_get_overwrites(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.set("mykey", "old_value")
        result = await manager.set_get("mykey", "new_value")
        assert result == "new_value"

    @pytest.mark.asyncio
    async def test_set_get_error(self, manager):
        mock_client = MagicMock()
        mock_client.pipeline.side_effect = Exception("error")
        manager.redis_client = mock_client
        result = await manager.set_get("mykey", "myvalue")
        assert result is None


class TestAsyncRedisPipelineManagerMgetPipeline:
    """Tests for mget_pipeline method."""

    @pytest.mark.asyncio
    async def test_mget_multiple_keys(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.set("key1", "value1")
        await async_client.set("key2", "value2")
        await async_client.set("key3", "value3")
        results = await manager.mget_pipeline("key1", "key2", "key3")
        assert results == ["value1", "value2", "value3"]

    @pytest.mark.asyncio
    async def test_mget_some_missing(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.set("key1", "value1")
        results = await manager.mget_pipeline("key1", "key2")
        assert results[0] == "value1"
        assert results[1] is None

    @pytest.mark.asyncio
    async def test_mget_all_missing(self, async_client, manager):
        manager.redis_client = async_client
        results = await manager.mget_pipeline("key1", "key2")
        assert results == [None, None]

    @pytest.mark.asyncio
    async def test_mget_empty(self, async_client, manager):
        manager.redis_client = async_client
        results = await manager.mget_pipeline()
        assert results == []

    @pytest.mark.asyncio
    async def test_mget_error(self, manager):
        mock_client = MagicMock()
        mock_client.pipeline.side_effect = Exception("error")
        manager.redis_client = mock_client
        results = await manager.mget_pipeline("key1")
        assert results == []


class TestAsyncRedisPipelineManagerMsetPipeline:
    """Tests for mset_pipeline method."""

    @pytest.mark.asyncio
    async def test_mset_multiple_keys(self, async_client, manager):
        manager.redis_client = async_client
        mapping = {"key1": "value1", "key2": "value2", "key3": "value3"}
        result = await manager.mset_pipeline(mapping)
        assert result is True
        assert await async_client.get("key1") == "value1"
        assert await async_client.get("key2") == "value2"
        assert await async_client.get("key3") == "value3"

    @pytest.mark.asyncio
    async def test_mset_single_key(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.mset_pipeline({"key1": "value1"})
        assert result is True
        assert await async_client.get("key1") == "value1"

    @pytest.mark.asyncio
    async def test_mset_empty_mapping(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.mset_pipeline({})
        assert result is True

    @pytest.mark.asyncio
    async def test_mset_overwrites_existing(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.set("key1", "old")
        result = await manager.mset_pipeline({"key1": "new"})
        assert result is True
        assert await async_client.get("key1") == "new"

    @pytest.mark.asyncio
    async def test_mset_error(self, manager):
        mock_client = MagicMock()
        mock_client.pipeline.side_effect = Exception("error")
        manager.redis_client = mock_client
        result = await manager.mset_pipeline({"key1": "value1"})
        assert result is False


class TestAsyncRedisPipelineManagerDeleteKeys:
    """Tests for delete_keys method."""

    @pytest.mark.asyncio
    async def test_delete_multiple_keys(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.set("key1", "value1")
        await async_client.set("key2", "value2")
        await async_client.set("key3", "value3")
        count = await manager.delete_keys("key1", "key2", "key3")
        assert count == 3

    @pytest.mark.asyncio
    async def test_delete_some_missing(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.set("key1", "value1")
        count = await manager.delete_keys("key1", "key2")
        assert count == 1

    @pytest.mark.asyncio
    async def test_delete_all_missing(self, async_client, manager):
        manager.redis_client = async_client
        count = await manager.delete_keys("key1", "key2")
        assert count == 0

    @pytest.mark.asyncio
    async def test_delete_no_keys(self, async_client, manager):
        manager.redis_client = async_client
        count = await manager.delete_keys()
        assert count == 0

    @pytest.mark.asyncio
    async def test_delete_error(self, manager):
        mock_client = MagicMock()
        mock_client.pipeline.side_effect = Exception("error")
        manager.redis_client = mock_client
        count = await manager.delete_keys("key1")
        assert count == 0
