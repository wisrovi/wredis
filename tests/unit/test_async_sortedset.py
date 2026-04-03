"""Tests for AsyncRedisSortedSetManager."""

import json
from unittest.mock import AsyncMock

import fakeredis.aioredis
import pytest

from wredis.async_api.sortedset import AsyncRedisSortedSetManager


@pytest.fixture
async def async_client():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=False)
    yield fake
    await fake.aclose()


@pytest.fixture
def manager():
    return AsyncRedisSortedSetManager(verbose=False)


class TestAsyncRedisSortedSetManagerInit:
    """Tests for initialization."""

    def test_init_defaults(self):
        m = AsyncRedisSortedSetManager()
        assert m.verbose is True

    def test_init_custom(self):
        m = AsyncRedisSortedSetManager(host="myhost", port=1234, db=2, verbose=False)
        assert m.verbose is False


class TestAsyncRedisSortedSetManagerAddToSortedSet:
    """Tests for add_to_sorted_set method."""

    @pytest.mark.asyncio
    async def test_add_member(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_sorted_set("myzset", 1.0, "member1")
        score = await async_client.zscore("myzset", "member1")
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_add_with_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_sorted_set("myzset", 1.0, "member1", ttl=60)
        ttl = await async_client.ttl("myzset")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_add_no_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_sorted_set("myzset", 1.0, "member1", ttl=-1)
        ttl = await async_client.ttl("myzset")
        assert ttl == -1

    @pytest.mark.asyncio
    async def test_add_update_score(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_sorted_set("myzset", 1.0, "member1")
        await manager.add_to_sorted_set("myzset", 5.0, "member1")
        score = await async_client.zscore("myzset", "member1")
        assert score == 5.0

    @pytest.mark.asyncio
    async def test_add_error(self, manager):
        mock_client = AsyncMock()
        mock_client.zadd.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.add_to_sorted_set("myzset", 1.0, "member1")


class TestAsyncRedisSortedSetManagerGetSortedSet:
    """Tests for get_sorted_set method."""

    @pytest.mark.asyncio
    async def test_get_all(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0, "b": 2.0, "c": 3.0})
        result = await manager.get_sorted_set("myzset")
        assert result == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_get_with_scores(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0, "b": 2.0})
        result = await manager.get_sorted_set("myzset", with_scores=True)
        assert result == [("a", 1.0), ("b", 2.0)]

    @pytest.mark.asyncio
    async def test_get_range(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0, "b": 2.0, "c": 3.0})
        result = await manager.get_sorted_set("myzset", start=0, stop=1)
        assert result == ["a", "b"]

    @pytest.mark.asyncio
    async def test_get_empty_set(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.get_sorted_set("nonexistent")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_error(self, manager):
        mock_client = AsyncMock()
        mock_client.zrange.side_effect = Exception("error")
        manager.redis_client = mock_client
        result = await manager.get_sorted_set("myzset")
        assert result == []


class TestAsyncRedisSortedSetManagerGetSortedSetReverse:
    """Tests for get_sorted_set_reverse method."""

    @pytest.mark.asyncio
    async def test_get_reverse(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0, "b": 2.0, "c": 3.0})
        result = await manager.get_sorted_set_reverse("myzset")
        assert result == ["c", "b", "a"]

    @pytest.mark.asyncio
    async def test_get_reverse_with_scores(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0, "b": 2.0})
        result = await manager.get_sorted_set_reverse("myzset", with_scores=True)
        assert result == [("b", 2.0), ("a", 1.0)]

    @pytest.mark.asyncio
    async def test_get_reverse_empty(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.get_sorted_set_reverse("nonexistent")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_reverse_error(self, manager):
        mock_client = AsyncMock()
        mock_client.zrevrange.side_effect = Exception("error")
        manager.redis_client = mock_client
        result = await manager.get_sorted_set_reverse("myzset")
        assert result == []


class TestAsyncRedisSortedSetManagerRemoveFromSortedSet:
    """Tests for remove_from_sorted_set method."""

    @pytest.mark.asyncio
    async def test_remove_existing(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0, "b": 2.0})
        await manager.remove_from_sorted_set("myzset", "a")
        result = await async_client.zrange("myzset", 0, -1)
        assert result == [b"b"]

    @pytest.mark.asyncio
    async def test_remove_nonexistent(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0})
        await manager.remove_from_sorted_set("myzset", "z")

    @pytest.mark.asyncio
    async def test_remove_error(self, manager):
        mock_client = AsyncMock()
        mock_client.zrem.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.remove_from_sorted_set("myzset", "a")


class TestAsyncRedisSortedSetManagerGetRank:
    """Tests for get_rank method."""

    @pytest.mark.asyncio
    async def test_get_rank(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0, "b": 2.0, "c": 3.0})
        rank = await manager.get_rank("myzset", "b")
        assert rank == 1

    @pytest.mark.asyncio
    async def test_get_rank_nonexistent_member(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0})
        rank = await manager.get_rank("myzset", "z")
        assert rank is None

    @pytest.mark.asyncio
    async def test_get_rank_error(self, manager):
        mock_client = AsyncMock()
        mock_client.zrank.side_effect = Exception("error")
        manager.redis_client = mock_client
        rank = await manager.get_rank("myzset", "a")
        assert rank is None


class TestAsyncRedisSortedSetManagerGetScore:
    """Tests for get_score method."""

    @pytest.mark.asyncio
    async def test_get_score(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0, "b": 2.5})
        score = await manager.get_score("myzset", "b")
        assert score == 2.5

    @pytest.mark.asyncio
    async def test_get_score_nonexistent_member(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0})
        score = await manager.get_score("myzset", "z")
        assert score is None

    @pytest.mark.asyncio
    async def test_get_score_error(self, manager):
        mock_client = AsyncMock()
        mock_client.zscore.side_effect = Exception("error")
        manager.redis_client = mock_client
        score = await manager.get_score("myzset", "a")
        assert score is None


class TestAsyncRedisSortedSetManagerDeleteSortedSet:
    """Tests for delete_sorted_set method."""

    @pytest.mark.asyncio
    async def test_delete_sorted_set(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0})
        await manager.delete_sorted_set("myzset")
        exists = await async_client.exists("myzset")
        assert exists == 0

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, async_client, manager):
        manager.redis_client = async_client
        await manager.delete_sorted_set("nonexistent")

    @pytest.mark.asyncio
    async def test_delete_error(self, manager):
        mock_client = AsyncMock()
        mock_client.delete.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.delete_sorted_set("myzset")


class TestAsyncRedisSortedSetManagerSetTTL:
    """Tests for set_ttl method."""

    @pytest.mark.asyncio
    async def test_set_ttl_existing(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0})
        await manager.set_ttl("myzset", 100)
        ttl = await async_client.ttl("myzset")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_set_ttl_nonexistent(self, async_client, manager):
        manager.redis_client = async_client
        await manager.set_ttl("nonexistent", 100)
        ttl = await async_client.ttl("nonexistent")
        assert ttl == -2

    @pytest.mark.asyncio
    async def test_set_ttl_error(self, manager):
        mock_client = AsyncMock()
        mock_client.exists.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.set_ttl("myzset", 100)


class TestAsyncRedisSortedSetManagerGetTTL:
    """Tests for get_ttl method."""

    @pytest.mark.asyncio
    async def test_get_ttl_with_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0})
        await async_client.expire("myzset", 100)
        ttl = await manager.get_ttl("myzset")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_get_ttl_no_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0})
        ttl = await manager.get_ttl("myzset")
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
        ttl = await manager.get_ttl("myzset")
        assert ttl is None


class TestAsyncRedisSortedSetManagerIncrementScore:
    """Tests for increment_score method."""

    @pytest.mark.asyncio
    async def test_increment_score(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0})
        await manager.increment_score("myzset", 2.5, "a")
        score = await async_client.zscore("myzset", "a")
        assert score == 3.5

    @pytest.mark.asyncio
    async def test_increment_score_new_member(self, async_client, manager):
        manager.redis_client = async_client
        await manager.increment_score("myzset", 5.0, "new_member")
        score = await async_client.zscore("myzset", "new_member")
        assert score == 5.0

    @pytest.mark.asyncio
    async def test_increment_negative(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 10.0})
        await manager.increment_score("myzset", -3.0, "a")
        score = await async_client.zscore("myzset", "a")
        assert score == 7.0

    @pytest.mark.asyncio
    async def test_increment_error(self, manager):
        mock_client = AsyncMock()
        mock_client.zincrby.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.increment_score("myzset", 1.0, "a")


class TestAsyncRedisSortedSetManagerGetSortedSetByScore:
    """Tests for get_sorted_set_by_score method."""

    @pytest.mark.asyncio
    async def test_get_by_score(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0, "b": 2.0, "c": 3.0, "d": 4.0})
        result = await manager.get_sorted_set_by_score("myzset", 1.5, 3.5)
        assert result == ["b", "c"]

    @pytest.mark.asyncio
    async def test_get_by_score_with_scores(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0, "b": 2.0})
        result = await manager.get_sorted_set_by_score("myzset", 0, 5, with_scores=True)
        assert result == [("a", 1.0), ("b", 2.0)]

    @pytest.mark.asyncio
    async def test_get_by_score_no_match(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0})
        result = await manager.get_sorted_set_by_score("myzset", 10, 20)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_score_error(self, manager):
        mock_client = AsyncMock()
        mock_client.zrangebyscore.side_effect = Exception("error")
        manager.redis_client = mock_client
        result = await manager.get_sorted_set_by_score("myzset", 0, 10)
        assert result == []


class TestAsyncRedisSortedSetManagerSetJson:
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


class TestAsyncRedisSortedSetManagerGetJson:
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


class TestAsyncRedisSortedSetManagerDeleteKey:
    """Tests for delete_key method."""

    @pytest.mark.asyncio
    async def test_delete_key_existing(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0})
        result = await manager.delete_key("myzset")
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
        result = await manager.delete_key("myzset")
        assert result is False
