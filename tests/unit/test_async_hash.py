"""Tests for AsyncRedisHashManager."""

import json
from unittest.mock import AsyncMock

import fakeredis.aioredis
import pytest

from wredis.async_api.hash import AsyncRedisHashManager


@pytest.fixture
async def async_client():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=False)
    yield fake
    await fake.aclose()


@pytest.fixture
def manager():
    return AsyncRedisHashManager(verbose=False)


class TestAsyncRedisHashManagerInit:
    """Tests for initialization."""

    def test_init_defaults(self):
        m = AsyncRedisHashManager()
        assert m.verbose is True

    def test_init_custom(self):
        m = AsyncRedisHashManager(host="myhost", port=1234, db=2, verbose=False)
        assert m.verbose is False


class TestAsyncRedisHashManagerCreateHash:
    """Tests for create_hash method."""

    @pytest.mark.asyncio
    async def test_create_hash_string_value(self, async_client, manager):
        manager.redis_client = async_client
        await manager.create_hash("myhash", "field1", "value1")
        val = await async_client.hget("myhash", "field1")
        assert val == b"value1"

    @pytest.mark.asyncio
    async def test_create_hash_dict_value(self, async_client, manager):
        manager.redis_client = async_client
        data = {"nested": "value"}
        await manager.create_hash("myhash", "field1", data)
        val = await async_client.hget("myhash", "field1")
        assert json.loads(val) == data

    @pytest.mark.asyncio
    async def test_create_hash_with_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await manager.create_hash("myhash", "field1", "value1", ttl=60)
        ttl = await async_client.ttl("myhash")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_create_hash_no_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await manager.create_hash("myhash", "field1", "value1", ttl=-1)
        ttl = await async_client.ttl("myhash")
        assert ttl == -1

    @pytest.mark.asyncio
    async def test_create_hash_error(self, manager):
        mock_client = AsyncMock()
        mock_client.hset.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.create_hash("myhash", "field1", "value1")
        mock_client.hset.assert_called_once()


class TestAsyncRedisHashManagerReadHash:
    """Tests for read_hash method."""

    @pytest.mark.asyncio
    async def test_read_hash_string(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.hset("myhash", "field1", "value1")
        val = await manager.read_hash("myhash", "field1")
        assert val == "value1"

    @pytest.mark.asyncio
    async def test_read_hash_dict(self, async_client, manager):
        manager.redis_client = async_client
        data = {"nested": "value"}
        await async_client.hset("myhash", "field1", json.dumps(data))
        val = await manager.read_hash("myhash", "field1")
        assert val == data

    @pytest.mark.asyncio
    async def test_read_hash_nonexistent_field(self, async_client, manager):
        manager.redis_client = async_client
        val = await manager.read_hash("myhash", "nonexistent")
        assert val is None

    @pytest.mark.asyncio
    async def test_read_hash_error(self, manager):
        mock_client = AsyncMock()
        mock_client.hget.side_effect = Exception("error")
        manager.redis_client = mock_client
        val = await manager.read_hash("myhash", "field1")
        assert val is None


class TestAsyncRedisHashManagerUpdateHash:
    """Tests for update_hash method."""

    @pytest.mark.asyncio
    async def test_update_hash_dict(self, async_client, manager):
        manager.redis_client = async_client
        await manager.create_hash("myhash", "field1", {"a": 1, "b": 2})
        await manager.update_hash("myhash", "field1", {"b": 3, "c": 4})
        val = await manager.read_hash("myhash", "field1")
        assert val == {"a": 1, "b": 3, "c": 4}

    @pytest.mark.asyncio
    async def test_update_hash_string_becomes_dict(self, async_client, manager):
        manager.redis_client = async_client
        await manager.create_hash("myhash", "field1", "plain_value")
        await manager.update_hash("myhash", "field1", {"new": "data"})
        val = await manager.read_hash("myhash", "field1")
        assert val == {"new": "data"}

    @pytest.mark.asyncio
    async def test_update_hash_error(self, manager):
        mock_client = AsyncMock()
        mock_client.hget.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.update_hash("myhash", "field1", {"a": 1})


class TestAsyncRedisHashManagerDeleteHashField:
    """Tests for delete_hash_field method."""

    @pytest.mark.asyncio
    async def test_delete_hash_field_existing(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.hset("myhash", "field1", "value1")
        await manager.delete_hash_field("myhash", "field1")
        val = await async_client.hget("myhash", "field1")
        assert val is None

    @pytest.mark.asyncio
    async def test_delete_hash_field_nonexistent(self, async_client, manager):
        manager.redis_client = async_client
        await manager.delete_hash_field("myhash", "nonexistent")

    @pytest.mark.asyncio
    async def test_delete_hash_field_error(self, manager):
        mock_client = AsyncMock()
        mock_client.hdel.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.delete_hash_field("myhash", "field1")


class TestAsyncRedisHashManagerReadAllHash:
    """Tests for read_all_hash method."""

    @pytest.mark.asyncio
    async def test_read_all_hash(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.hset("myhash", "field1", "value1")
        await async_client.hset("myhash", "field2", json.dumps({"a": 1}))
        result = await manager.read_all_hash("myhash")
        assert result["field1"] == "value1"
        assert result["field2"] == {"a": 1}

    @pytest.mark.asyncio
    async def test_read_all_hash_empty(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.read_all_hash("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_read_all_hash_error(self, manager):
        mock_client = AsyncMock()
        mock_client.hgetall.side_effect = Exception("error")
        manager.redis_client = mock_client
        result = await manager.read_all_hash("myhash")
        assert result is None


class TestAsyncRedisHashManagerGetTTL:
    """Tests for get_ttl method."""

    @pytest.mark.asyncio
    async def test_get_ttl_with_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.hset("myhash", "f", "v")
        await async_client.expire("myhash", 100)
        ttl = await manager.get_ttl("myhash")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_get_ttl_no_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.hset("myhash", "f", "v")
        ttl = await manager.get_ttl("myhash")
        assert ttl == -1

    @pytest.mark.asyncio
    async def test_get_ttl_nonexistent(self, async_client, manager):
        manager.redis_client = async_client
        ttl = await manager.get_ttl("nonexistent")
        assert ttl == -2

    @pytest.mark.asyncio
    async def test_get_ttl_error(self, manager):
        mock_client = AsyncMock()
        mock_client.ttl.side_effect = Exception("error")
        manager.redis_client = mock_client
        ttl = await manager.get_ttl("myhash")
        assert ttl is None


class TestAsyncRedisHashManagerExtendTTL:
    """Tests for extend_ttl method."""

    @pytest.mark.asyncio
    async def test_extend_ttl_existing(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.hset("myhash", "f", "v")
        await manager.extend_ttl("myhash", 200)
        ttl = await async_client.ttl("myhash")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_extend_ttl_nonexistent(self, async_client, manager):
        manager.redis_client = async_client
        await manager.extend_ttl("nonexistent", 200)
        ttl = await async_client.ttl("nonexistent")
        assert ttl == -2

    @pytest.mark.asyncio
    async def test_extend_ttl_error(self, manager):
        mock_client = AsyncMock()
        mock_client.exists.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.extend_ttl("myhash", 100)


class TestAsyncRedisHashManagerSetJson:
    """Tests for set_json method."""

    @pytest.mark.asyncio
    async def test_set_json(self, async_client, manager):
        manager.redis_client = async_client
        data = {"key": "value"}
        await manager.set_json("mykey", data)
        raw = await async_client.get("mykey")
        assert json.loads(raw) == data

    @pytest.mark.asyncio
    async def test_set_json_with_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await manager.set_json("mykey", {"a": 1}, ttl=60)
        ttl = await async_client.ttl("mykey")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_set_json_error(self, manager):
        mock_client = AsyncMock()
        mock_client.set.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.set_json("mykey", {"a": 1})


class TestAsyncRedisHashManagerGetJson:
    """Tests for get_json method."""

    @pytest.mark.asyncio
    async def test_get_json_existing(self, async_client, manager):
        manager.redis_client = async_client
        data = {"key": "value"}
        await async_client.set("mykey", json.dumps(data))
        result = await manager.get_json("mykey")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_json_nonexistent(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.get_json("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_json_error(self, manager):
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("error")
        manager.redis_client = mock_client
        result = await manager.get_json("mykey")
        assert result is None


class TestAsyncRedisHashManagerDeleteKey:
    """Tests for delete_key method."""

    @pytest.mark.asyncio
    async def test_delete_key_existing(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.hset("myhash", "f", "v")
        result = await manager.delete_key("myhash")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_key_nonexistent(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.delete_key("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_key_error(self, manager):
        mock_client = AsyncMock()
        mock_client.delete.side_effect = Exception("error")
        manager.redis_client = mock_client
        result = await manager.delete_key("myhash")
        assert result is False
