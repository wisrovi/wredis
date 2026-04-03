"""Tests for AsyncRedisBitmapManager."""

import json
from unittest.mock import AsyncMock, patch

import fakeredis.aioredis
import pytest

from wredis.async_api.bitmap import AsyncRedisBitmapManager


@pytest.fixture
async def async_client():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield fake
    await fake.aclose()


@pytest.fixture
def manager():
    return AsyncRedisBitmapManager(verbose=False)


class TestAsyncRedisBitmapManagerInit:
    """Tests for AsyncRedisBitmapManager initialization."""

    def test_init_defaults(self):
        m = AsyncRedisBitmapManager()
        assert m.verbose is True

    def test_init_custom(self):
        m = AsyncRedisBitmapManager(host="myhost", port=1234, db=2, verbose=False)
        assert m.verbose is False


class TestAsyncRedisBitmapManagerSetBit:
    """Tests for set_bit method."""

    @pytest.mark.asyncio
    async def test_set_bit_basic(self, async_client, manager):
        manager.redis_client = async_client
        await manager.set_bit("mybitmap", 0, 1)
        val = await async_client.getbit("mybitmap", 0)
        assert val == 1

    @pytest.mark.asyncio
    async def test_set_bit_to_zero(self, async_client, manager):
        manager.redis_client = async_client
        await manager.set_bit("mybitmap", 5, 0)
        val = await async_client.getbit("mybitmap", 5)
        assert val == 0

    @pytest.mark.asyncio
    async def test_set_bit_with_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await manager.set_bit("mybitmap", 0, 1, ttl=60)
        ttl = await async_client.ttl("mybitmap")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_set_bit_no_ttl_when_negative(self, async_client, manager):
        manager.redis_client = async_client
        await manager.set_bit("mybitmap", 0, 1, ttl=-1)
        ttl = await async_client.ttl("mybitmap")
        assert ttl == -1

    @pytest.mark.asyncio
    async def test_set_bit_error_handling(self, manager):
        mock_client = AsyncMock()
        mock_client.setbit.side_effect = Exception("connection error")
        manager.redis_client = mock_client
        await manager.set_bit("mybitmap", 0, 1)
        mock_client.setbit.assert_called_once_with("mybitmap", 0, 1)


class TestAsyncRedisBitmapManagerGetBit:
    """Tests for get_bit method."""

    @pytest.mark.asyncio
    async def test_get_bit_set(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.setbit("mybitmap", 3, 1)
        val = await manager.get_bit("mybitmap", 3)
        assert val == 1

    @pytest.mark.asyncio
    async def test_get_bit_unset(self, async_client, manager):
        manager.redis_client = async_client
        val = await manager.get_bit("mybitmap", 100)
        assert val == 0

    @pytest.mark.asyncio
    async def test_get_bit_error_returns_zero(self, manager):
        mock_client = AsyncMock()
        mock_client.getbit.side_effect = Exception("redis error")
        manager.redis_client = mock_client
        val = await manager.get_bit("mybitmap", 0)
        assert val == 0


class TestAsyncRedisBitmapManagerCountBits:
    """Tests for count_bits method."""

    @pytest.mark.asyncio
    async def test_count_bits(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.setbit("mybitmap", 0, 1)
        await async_client.setbit("mybitmap", 5, 1)
        await async_client.setbit("mybitmap", 10, 1)
        count = await manager.count_bits("mybitmap")
        assert count == 3

    @pytest.mark.asyncio
    async def test_count_bits_empty(self, async_client, manager):
        manager.redis_client = async_client
        count = await manager.count_bits("nonexistent")
        assert count == 0

    @pytest.mark.asyncio
    async def test_count_bits_error_returns_zero(self, manager):
        mock_client = AsyncMock()
        mock_client.bitcount.side_effect = Exception("error")
        manager.redis_client = mock_client
        count = await manager.count_bits("mybitmap")
        assert count == 0


class TestAsyncRedisBitmapManagerGetTTL:
    """Tests for get_ttl method."""

    @pytest.mark.asyncio
    async def test_get_ttl_with_ttl_set(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.setbit("mybitmap", 0, 1)
        await async_client.expire("mybitmap", 100)
        ttl = await manager.get_ttl("mybitmap")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_get_ttl_no_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.setbit("mybitmap", 0, 1)
        ttl = await manager.get_ttl("mybitmap")
        assert ttl == -1

    @pytest.mark.asyncio
    async def test_get_ttl_nonexistent_key(self, async_client, manager):
        manager.redis_client = async_client
        ttl = await manager.get_ttl("nonexistent")
        assert ttl == -2

    @pytest.mark.asyncio
    async def test_get_ttl_error(self, manager):
        mock_client = AsyncMock()
        mock_client.ttl.side_effect = Exception("error")
        manager.redis_client = mock_client
        ttl = await manager.get_ttl("mybitmap")
        assert ttl == -2


class TestAsyncRedisBitmapManagerExtendTTL:
    """Tests for extend_ttl method."""

    @pytest.mark.asyncio
    async def test_extend_ttl_existing_key(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.setbit("mybitmap", 0, 1)
        await manager.extend_ttl("mybitmap", 200)
        ttl = await async_client.ttl("mybitmap")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_extend_ttl_nonexistent_key(self, async_client, manager):
        manager.redis_client = async_client
        await manager.extend_ttl("nonexistent", 200)
        ttl = await async_client.ttl("nonexistent")
        assert ttl == -2

    @pytest.mark.asyncio
    async def test_extend_ttl_error(self, manager):
        mock_client = AsyncMock()
        mock_client.exists.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.extend_ttl("mybitmap", 100)
        mock_client.exists.assert_called_once_with("mybitmap")


class TestAsyncRedisBitmapManagerSetJson:
    """Tests for set_json method."""

    @pytest.mark.asyncio
    async def test_set_json_dict(self, async_client, manager):
        manager.redis_client = async_client
        data = {"name": "test", "value": 42}
        await manager.set_json("mykey", data)
        raw = await async_client.get("mykey")
        assert json.loads(raw) == data

    @pytest.mark.asyncio
    async def test_set_json_list(self, async_client, manager):
        manager.redis_client = async_client
        data = [1, 2, 3]
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


class TestAsyncRedisBitmapManagerGetJson:
    """Tests for get_json method."""

    @pytest.mark.asyncio
    async def test_get_json_existing(self, async_client, manager):
        manager.redis_client = async_client
        data = {"name": "test"}
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


class TestAsyncRedisBitmapManagerDeleteKey:
    """Tests for delete_key method."""

    @pytest.mark.asyncio
    async def test_delete_key_existing(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.setbit("mybitmap", 0, 1)
        result = await manager.delete_key("mybitmap")
        assert result is True
        exists = await async_client.exists("mybitmap")
        assert exists == 0

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
        result = await manager.delete_key("mybitmap")
        assert result is False
