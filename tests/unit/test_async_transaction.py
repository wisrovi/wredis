"""Tests for AsyncRedisTransactionManager."""

from unittest.mock import AsyncMock, MagicMock

import fakeredis.aioredis
import pytest

from wredis.async_api.transaction import AsyncRedisTransactionManager


@pytest.fixture
async def async_client():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield fake
    await fake.aclose()


@pytest.fixture
def manager():
    return AsyncRedisTransactionManager(verbose=False)


class TestAsyncRedisTransactionManagerInit:
    """Tests for initialization."""

    def test_init_defaults(self):
        m = AsyncRedisTransactionManager()
        assert m.verbose is True

    def test_init_custom(self):
        m = AsyncRedisTransactionManager(host="myhost", port=1234, db=2, verbose=False)
        assert m.verbose is False


class TestAsyncRedisTransactionManagerExecuteTransaction:
    """Tests for execute_transaction method."""

    @pytest.mark.asyncio
    async def test_execute_transaction_basic(self, async_client, manager):
        manager.redis_client = async_client
        commands = [
            ("set", ["key1", "value1"]),
            ("set", ["key2", "value2"]),
            ("get", ["key1"]),
        ]
        results = await manager.execute_transaction(commands)
        assert results is not None
        assert results[0] is True
        assert results[1] is True
        assert results[2] == "value1"

    @pytest.mark.asyncio
    async def test_execute_transaction_empty(self, async_client, manager):
        manager.redis_client = async_client
        results = await manager.execute_transaction([])
        assert results is not None
        assert results == []

    @pytest.mark.asyncio
    async def test_execute_transaction_hash_ops(self, async_client, manager):
        manager.redis_client = async_client
        commands = [
            ("hset", ["myhash", "field", "value"]),
            ("hget", ["myhash", "field"]),
        ]
        results = await manager.execute_transaction(commands)
        assert results is not None
        assert results[0] == 1
        assert results[1] == "value"

    @pytest.mark.asyncio
    async def test_execute_transaction_list_ops(self, async_client, manager):
        manager.redis_client = async_client
        commands = [
            ("rpush", ["mylist", "a", "b", "c"]),
            ("llen", ["mylist"]),
        ]
        results = await manager.execute_transaction(commands)
        assert results is not None
        assert results[0] == 3
        assert results[1] == 3

    @pytest.mark.asyncio
    async def test_execute_transaction_error(self, manager):
        mock_client = MagicMock()
        mock_client.pipeline.side_effect = Exception("connection error")
        manager.redis_client = mock_client
        results = await manager.execute_transaction([("set", ["k", "v"])])
        assert results is None


class TestAsyncRedisTransactionManagerSetIfNotExists:
    """Tests for set_if_not_exists method."""

    @pytest.mark.asyncio
    async def test_set_if_not_exists_new_key(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.set_if_not_exists("mykey", "myvalue")
        assert result is True
        assert await async_client.get("mykey") == "myvalue"

    @pytest.mark.asyncio
    async def test_set_if_not_exists_existing_key(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.set("mykey", "existing")
        result = await manager.set_if_not_exists("mykey", "newvalue")
        assert result is False
        assert await async_client.get("mykey") == "existing"

    @pytest.mark.asyncio
    async def test_set_if_not_exists_with_ttl(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.set_if_not_exists("mykey", "myvalue", ttl=60)
        assert result is True
        ttl = await async_client.ttl("mykey")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_set_if_not_exists_no_ttl(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.set_if_not_exists("mykey", "myvalue", ttl=-1)
        assert result is True
        ttl = await async_client.ttl("mykey")
        assert ttl == -1

    @pytest.mark.asyncio
    async def test_set_if_not_exists_error(self, manager):
        mock_client = AsyncMock()
        mock_client.set.side_effect = Exception("error")
        manager.redis_client = mock_client
        result = await manager.set_if_not_exists("mykey", "myvalue")
        assert result is False


class TestAsyncRedisTransactionManagerIncrementAtomic:
    """Tests for increment_atomic method."""

    @pytest.mark.asyncio
    async def test_increment_positive(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.set("counter", 10)
        result = await manager.increment_atomic("counter", 5)
        assert result == 15

    @pytest.mark.asyncio
    async def test_increment_default_amount(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.set("counter", 0)
        result = await manager.increment_atomic("counter")
        assert result == 1

    @pytest.mark.asyncio
    async def test_increment_negative_decrements(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.set("counter", 10)
        result = await manager.increment_atomic("counter", -3)
        assert result == 7

    @pytest.mark.asyncio
    async def test_increment_new_key(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.increment_atomic("counter", 5)
        assert result == 5

    @pytest.mark.asyncio
    async def test_increment_negative_new_key(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.increment_atomic("counter", -5)
        assert result == -5

    @pytest.mark.asyncio
    async def test_increment_zero_amount(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.set("counter", 10)
        result = await manager.increment_atomic("counter", 0)
        assert result == 10

    @pytest.mark.asyncio
    async def test_increment_error(self, manager):
        mock_client = AsyncMock()
        mock_client.incrby.side_effect = Exception("error")
        manager.redis_client = mock_client
        result = await manager.increment_atomic("counter", 5)
        assert result == 0


class TestAsyncRedisTransactionManagerGetAndSet:
    """Tests for get_and_set method."""

    @pytest.mark.asyncio
    async def test_get_and_set_existing(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.set("mykey", "old_value")
        result = await manager.get_and_set("mykey", "new_value")
        assert result == "old_value"
        assert await async_client.get("mykey") == "new_value"

    @pytest.mark.asyncio
    async def test_get_and_set_nonexistent(self, async_client, manager):
        manager.redis_client = async_client
        result = await manager.get_and_set("mykey", "new_value")
        assert result is None
        assert await async_client.get("mykey") == "new_value"

    @pytest.mark.asyncio
    async def test_get_and_set_error(self, manager):
        mock_client = MagicMock()
        mock_client.pipeline.side_effect = Exception("error")
        manager.redis_client = mock_client
        result = await manager.get_and_set("mykey", "new_value")
        assert result is None
