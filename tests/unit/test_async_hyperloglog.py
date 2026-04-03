"""Tests for AsyncRedisHyperLogLogManager."""

from unittest.mock import AsyncMock

import fakeredis.aioredis
import pytest

from wredis.async_api.hyperloglog import AsyncRedisHyperLogLogManager


@pytest.fixture
async def async_client():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield fake
    await fake.aclose()


@pytest.fixture
def manager():
    return AsyncRedisHyperLogLogManager(verbose=False)


class TestAsyncRedisHyperLogLogManagerInit:
    """Tests for initialization."""

    def test_init_defaults(self):
        m = AsyncRedisHyperLogLogManager()
        assert m.verbose is True

    def test_init_custom(self):
        m = AsyncRedisHyperLogLogManager(host="myhost", port=1234, db=2, verbose=False)
        assert m.verbose is False


class TestAsyncRedisHyperLogLogManagerAdd:
    """Tests for add method."""

    @pytest.mark.asyncio
    async def test_add_single_value(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add("myhll", "user1")
        count = await async_client.pfcount("myhll")
        assert count == 1

    @pytest.mark.asyncio
    async def test_add_multiple_values(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add("myhll", "user1", "user2", "user3")
        count = await async_client.pfcount("myhll")
        assert count == 3

    @pytest.mark.asyncio
    async def test_add_duplicates(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add("myhll", "user1", "user1", "user1")
        count = await async_client.pfcount("myhll")
        assert count == 1

    @pytest.mark.asyncio
    async def test_add_to_existing(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add("myhll", "user1")
        await manager.add("myhll", "user2")
        count = await async_client.pfcount("myhll")
        assert count == 2

    @pytest.mark.asyncio
    async def test_add_many_unique(self, async_client, manager):
        manager.redis_client = async_client
        users = [f"user{i}" for i in range(100)]
        await manager.add("myhll", *users)
        count = await async_client.pfcount("myhll")
        assert count == 100

    @pytest.mark.asyncio
    async def test_add_error(self, manager):
        mock_client = AsyncMock()
        mock_client.pfadd.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.add("myhll", "user1")
        mock_client.pfadd.assert_called_once_with("myhll", "user1")


class TestAsyncRedisHyperLogLogManagerCount:
    """Tests for count method."""

    @pytest.mark.asyncio
    async def test_count_single_key(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add("myhll", "user1", "user2", "user3")
        count = await manager.count("myhll")
        assert count == 3

    @pytest.mark.asyncio
    async def test_count_empty_key(self, async_client, manager):
        manager.redis_client = async_client
        count = await manager.count("nonexistent")
        assert count == 0

    @pytest.mark.asyncio
    async def test_count_multiple_keys(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add("hll1", "user1", "user2")
        await manager.add("hll2", "user3", "user4")
        count = await manager.count("hll1", "hll2")
        assert count == 4

    @pytest.mark.asyncio
    async def test_count_with_overlap(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add("hll1", "user1", "user2")
        await manager.add("hll2", "user2", "user3")
        count = await manager.count("hll1", "hll2")
        assert count == 3

    @pytest.mark.asyncio
    async def test_count_error(self, manager):
        mock_client = AsyncMock()
        mock_client.pfcount.side_effect = Exception("error")
        manager.redis_client = mock_client
        count = await manager.count("myhll")
        assert count == 0


class TestAsyncRedisHyperLogLogManagerMerge:
    """Tests for merge method."""

    @pytest.mark.asyncio
    async def test_merge_two_keys(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add("hll1", "user1", "user2")
        await manager.add("hll2", "user3", "user4")
        await manager.merge("merged", "hll1", "hll2")
        count = await async_client.pfcount("merged")
        assert count == 4

    @pytest.mark.asyncio
    async def test_merge_with_overlap(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add("hll1", "user1", "user2")
        await manager.add("hll2", "user2", "user3")
        await manager.merge("merged", "hll1", "hll2")
        count = await async_client.pfcount("merged")
        assert count == 3

    @pytest.mark.asyncio
    async def test_merge_multiple_sources(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add("hll1", "a")
        await manager.add("hll2", "b")
        await manager.add("hll3", "c")
        await manager.merge("merged", "hll1", "hll2", "hll3")
        count = await async_client.pfcount("merged")
        assert count == 3

    @pytest.mark.asyncio
    async def test_merge_into_existing_destination(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add("hll1", "user1")
        await manager.add("hll2", "user2")
        await manager.add("merged", "user3")
        await manager.merge("merged", "hll1", "hll2")
        count = await async_client.pfcount("merged")
        assert count >= 2

    @pytest.mark.asyncio
    async def test_merge_empty_sources(self, async_client, manager):
        manager.redis_client = async_client
        await manager.merge("merged")
        count = await async_client.pfcount("merged")
        assert count == 0

    @pytest.mark.asyncio
    async def test_merge_error(self, manager):
        mock_client = AsyncMock()
        mock_client.pfmerge.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.merge("merged", "hll1", "hll2")
        mock_client.pfmerge.assert_called_once_with("merged", "hll1", "hll2")
