"""Tests for AsyncRedisSetManager."""

import json
from unittest.mock import AsyncMock

import fakeredis.aioredis
import pytest

from wredis.async_api.sets import AsyncRedisSetManager


@pytest.fixture
async def async_client():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=False)
    yield fake
    await fake.aclose()


@pytest.fixture
def manager():
    return AsyncRedisSetManager(verbose=False)


class TestAsyncRedisSetManagerInit:
    """Tests for initialization."""

    def test_init_defaults(self):
        m = AsyncRedisSetManager()
        assert m.verbose is True

    def test_init_custom(self):
        m = AsyncRedisSetManager(host="myhost", port=1234, db=2, verbose=False)
        assert m.verbose is False


class TestAsyncRedisSetManagerAddToSet:
    """Tests for add_to_set method."""

    @pytest.mark.asyncio
    async def test_add_single_value(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_set("myset", "member1")
        members = await async_client.smembers("myset")
        assert b"member1" in members

    @pytest.mark.asyncio
    async def test_add_multiple_values(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_set("myset", "a", "b", "c")
        members = await async_client.smembers("myset")
        assert members == {b"a", b"b", b"c"}

    @pytest.mark.asyncio
    async def test_add_with_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_set("myset", "member1", ttl=60)
        ttl = await async_client.ttl("myset")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_add_no_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_set("myset", "member1", ttl=-1)
        ttl = await async_client.ttl("myset")
        assert ttl == -1

    @pytest.mark.asyncio
    async def test_add_duplicate(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_set("myset", "member1")
        await manager.add_to_set("myset", "member1")
        members = await async_client.smembers("myset")
        assert members == {b"member1"}

    @pytest.mark.asyncio
    async def test_add_error(self, manager):
        mock_client = AsyncMock()
        mock_client.sadd.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.add_to_set("myset", "member1")


class TestAsyncRedisSetManagerGetSetMembers:
    """Tests for get_set_members method."""

    @pytest.mark.asyncio
    async def test_get_members(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.sadd("myset", "a", "b", "c")
        members = await manager.get_set_members("myset")
        assert members == {"a", "b", "c"}

    @pytest.mark.asyncio
    async def test_get_members_empty(self, async_client, manager):
        manager.redis_client = async_client
        members = await manager.get_set_members("nonexistent")
        assert members == set()

    @pytest.mark.asyncio
    async def test_get_members_error(self, manager):
        mock_client = AsyncMock()
        mock_client.smembers.side_effect = Exception("error")
        manager.redis_client = mock_client
        members = await manager.get_set_members("myset")
        assert members == set()


class TestAsyncRedisSetManagerIsMember:
    """Tests for is_member method."""

    @pytest.mark.asyncio
    async def test_is_member_true(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.sadd("myset", "member1")
        result = await manager.is_member("myset", "member1")
        assert bool(result) is True

    @pytest.mark.asyncio
    async def test_is_member_false(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.sadd("myset", "member1")
        result = await manager.is_member("myset", "member2")
        assert bool(result) is False

    @pytest.mark.asyncio
    async def test_is_member_nonexistent_set(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.is_member("nonexistent", "member1")
        assert bool(result) is False

    @pytest.mark.asyncio
    async def test_is_member_error(self, manager):
        mock_client = AsyncMock()
        mock_client.sismember.side_effect = Exception("error")
        manager.redis_client = mock_client
        result = await manager.is_member("myset", "member1")
        assert result is False


class TestAsyncRedisSetManagerRemoveFromSet:
    """Tests for remove_from_set method."""

    @pytest.mark.asyncio
    async def test_remove_single(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.sadd("myset", "a", "b", "c")
        await manager.remove_from_set("myset", "b")
        members = await async_client.smembers("myset")
        assert members == {b"a", b"c"}

    @pytest.mark.asyncio
    async def test_remove_multiple(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.sadd("myset", "a", "b", "c")
        await manager.remove_from_set("myset", "a", "c")
        members = await async_client.smembers("myset")
        assert members == {b"b"}

    @pytest.mark.asyncio
    async def test_remove_nonexistent_member(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.sadd("myset", "a")
        await manager.remove_from_set("myset", "z")
        members = await async_client.smembers("myset")
        assert members == {b"a"}

    @pytest.mark.asyncio
    async def test_remove_error(self, manager):
        mock_client = AsyncMock()
        mock_client.srem.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.remove_from_set("myset", "a")


class TestAsyncRedisSetManagerGetTTL:
    """Tests for get_ttl method."""

    @pytest.mark.asyncio
    async def test_get_ttl_with_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.sadd("myset", "a")
        await async_client.expire("myset", 100)
        ttl = await manager.get_ttl("myset")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_get_ttl_no_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.sadd("myset", "a")
        ttl = await manager.get_ttl("myset")
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
        ttl = await manager.get_ttl("myset")
        assert ttl is None


class TestAsyncRedisSetManagerExtendTTL:
    """Tests for extend_ttl method."""

    @pytest.mark.asyncio
    async def test_extend_ttl_existing(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.sadd("myset", "a")
        await manager.extend_ttl("myset", 200)
        ttl = await async_client.ttl("myset")
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
        await manager.extend_ttl("myset", 100)


class TestAsyncRedisSetManagerSetJson:
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


class TestAsyncRedisSetManagerGetJson:
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


class TestAsyncRedisSetManagerDeleteKey:
    """Tests for delete_key method."""

    @pytest.mark.asyncio
    async def test_delete_key_existing(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.sadd("myset", "a")
        result = await manager.delete_key("myset")
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
        result = await manager.delete_key("myset")
        assert result is False
