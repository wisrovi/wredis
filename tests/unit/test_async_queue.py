"""Tests for AsyncRedisQueueManager."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import fakeredis.aioredis
import pytest
import redis.asyncio as aredis

from wredis._exceptions import QueueError, ValidationError
from wredis.async_api.queue import AsyncRedisQueueManager


@pytest.fixture
async def async_client():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=False)
    yield fake
    await fake.aclose()


@pytest.fixture
def manager():
    return AsyncRedisQueueManager(poll_interval=1, verbose=False)


class TestAsyncQueueInit:
    """Tests for initialization."""

    def test_init_defaults(self):
        m = AsyncRedisQueueManager()
        assert m.poll_interval == 1
        assert m.callbacks == {}
        assert m._tasks == {}
        assert m.running is False
        assert m.max_retries == 3
        assert m.verbose is True

    def test_init_custom(self):
        m = AsyncRedisQueueManager(
            poll_interval=5,
            host="myhost",
            port=1234,
            db=2,
            max_retries=10,
            verbose=False,
        )
        assert m.poll_interval == 5
        assert m.max_retries == 10
        assert m.verbose is False


class TestAsyncQueueOnMessage:
    """Tests for on_message decorator."""

    def test_on_message_registers_callback(self, manager):
        @manager.on_message("test_queue")
        async def handler(data):
            pass

        assert "test_queue" in manager.callbacks
        assert manager.callbacks["test_queue"] is handler

    def test_on_message_duplicate_raises(self, manager):
        @manager.on_message("test_queue")
        async def handler1(data):
            pass

        with pytest.raises(QueueError):

            @manager.on_message("test_queue")
            async def handler2(data):
                pass

    def test_on_message_invalid_queue_name_raises(self, manager):
        with pytest.raises(ValidationError):

            @manager.on_message("")
            async def handler(data):
                pass

    def test_on_message_sync_callback(self, manager):
        @manager.on_message("test_queue")
        def handler(data):
            pass

        assert "test_queue" in manager.callbacks


class TestAsyncQueuePublish:
    """Tests for publish method."""

    @pytest.mark.asyncio
    async def test_publish_dict_message(self, async_client, manager):
        manager.redis_client = async_client
        data = {"key": "value", "num": 42}
        await manager.publish("test_queue", data)
        length = await async_client.llen("test_queue")
        assert length == 1

    @pytest.mark.asyncio
    async def test_publish_invalid_queue_name(self, manager):
        manager.redis_client = AsyncMock()
        with pytest.raises(ValidationError):
            await manager.publish("", {"key": "value"})

    @pytest.mark.asyncio
    async def test_publish_invalid_ttl(self, manager):
        manager.redis_client = AsyncMock()
        with pytest.raises(ValidationError):
            await manager.publish("test_queue", {"key": "value"}, ttl=-2)

    @pytest.mark.asyncio
    async def test_publish_with_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await manager.publish("test_queue", {"key": "value"}, ttl=60)
        ttl = await async_client.ttl("test_queue")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_publish_without_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await manager.publish("test_queue", {"key": "value"}, ttl=-1)
        ttl = await async_client.ttl("test_queue")
        assert ttl == -1

    @pytest.mark.asyncio
    async def test_publish_redis_error(self, manager):
        mock_client = AsyncMock()
        mock_client.rpush.side_effect = aredis.RedisError("connection lost")
        manager.redis_client = mock_client
        with pytest.raises(QueueError):
            await manager.publish("test_queue", {"key": "value"})

    @pytest.mark.asyncio
    async def test_publish_multiple_messages(self, async_client, manager):
        manager.redis_client = async_client
        await manager.publish("test_queue", {"msg": 1})
        await manager.publish("test_queue", {"msg": 2})
        await manager.publish("test_queue", {"msg": 3})
        length = await async_client.llen("test_queue")
        assert length == 3


class TestAsyncQueueGetQueueLength:
    """Tests for get_queue_length method."""

    @pytest.mark.asyncio
    async def test_get_queue_length_empty(self, async_client, manager):
        manager.redis_client = async_client
        length = await manager.get_queue_length("empty_queue")
        assert length == 0

    @pytest.mark.asyncio
    async def test_get_queue_length_with_items(self, async_client, manager):
        manager.redis_client = async_client
        await async_client.rpush("test_queue", "item1", "item2", "item3")
        length = await manager.get_queue_length("test_queue")
        assert length == 3

    @pytest.mark.asyncio
    async def test_get_queue_length_invalid_name(self, manager):
        manager.redis_client = AsyncMock()
        with pytest.raises(ValidationError):
            await manager.get_queue_length("")

    @pytest.mark.asyncio
    async def test_get_queue_length_redis_error(self, manager):
        mock_client = AsyncMock()
        mock_client.llen.side_effect = aredis.RedisError("connection lost")
        manager.redis_client = mock_client
        with pytest.raises(QueueError):
            await manager.get_queue_length("test_queue")


class TestAsyncQueueStart:
    """Tests for start method."""

    @pytest.mark.asyncio
    async def test_start_creates_tasks(self, async_client, manager):
        @manager.on_message("test_queue")
        async def handler(data):
            pass

        manager.redis_client = async_client
        await manager.start()
        assert manager.running is True
        assert len(manager._tasks) == 1
        assert "test_queue" in manager._tasks
        await manager.stop()

    @pytest.mark.asyncio
    async def test_start_no_callbacks_raises(self, manager):
        manager.redis_client = AsyncMock()
        with pytest.raises(QueueError):
            await manager.start()

    @pytest.mark.asyncio
    async def test_start_already_running(self, async_client, manager):
        @manager.on_message("test_queue")
        async def handler(data):
            pass

        manager.redis_client = async_client
        await manager.start()
        await manager.start()
        assert manager.running is True
        await manager.stop()

    @pytest.mark.asyncio
    async def test_start_multiple_queues(self, async_client, manager):
        @manager.on_message("q1")
        async def h1(data):
            pass

        @manager.on_message("q2")
        async def h2(data):
            pass

        manager.redis_client = async_client
        await manager.start()
        assert len(manager._tasks) == 2
        await manager.stop()


class TestAsyncQueueStop:
    """Tests for stop method."""

    @pytest.mark.asyncio
    async def test_stop_cancels_tasks(self, async_client, manager):
        @manager.on_message("test_queue")
        async def handler(data):
            pass

        manager.redis_client = async_client
        await manager.start()
        await manager.stop()
        assert manager.running is False
        assert len(manager._tasks) == 0

    @pytest.mark.asyncio
    async def test_stop_already_stopped(self, manager):
        manager.redis_client = AsyncMock()
        await manager.stop()


class TestAsyncQueueConsume:
    """Tests for queue consumption with callback."""

    @pytest.mark.asyncio
    async def test_consume_with_async_callback(self, async_client, manager):
        received = []

        @manager.on_message("test_queue")
        async def handler(data):
            received.append(data)

        manager.redis_client = async_client
        manager.poll_interval = 0.1
        await manager.start()
        await asyncio.sleep(0.1)

        await manager.publish("test_queue", {"action": "test"})
        await asyncio.sleep(1.0)

        await manager.stop()
        assert len(received) >= 1
        assert received[0] == {"action": "test"}

    @pytest.mark.asyncio
    async def test_consume_with_sync_callback(self, async_client, manager):
        received = []

        @manager.on_message("test_queue")
        def handler(data):
            received.append(data)

        manager.redis_client = async_client
        manager.poll_interval = 0.1
        await manager.start()
        await asyncio.sleep(0.1)

        await manager.publish("test_queue", {"action": "sync"})
        await asyncio.sleep(1.0)

        await manager.stop()
        assert len(received) >= 1
        assert received[0] == {"action": "sync"}

    @pytest.mark.asyncio
    async def test_consume_multiple_messages(self, async_client, manager):
        received = []

        @manager.on_message("test_queue")
        async def handler(data):
            received.append(data)

        manager.redis_client = async_client
        manager.poll_interval = 0.1
        await manager.start()
        await asyncio.sleep(0.1)

        await manager.publish("test_queue", {"msg": 1})
        await manager.publish("test_queue", {"msg": 2})
        await asyncio.sleep(1.0)

        await manager.stop()
        assert len(received) >= 2


class TestAsyncQueueClose:
    """Tests for close method."""

    @pytest.mark.asyncio
    async def test_close_stops_and_closes(self, async_client, manager):
        @manager.on_message("test_queue")
        async def handler(data):
            pass

        manager.redis_client = async_client
        await manager.start()
        await manager.close()
        assert manager.running is False
        assert len(manager._tasks) == 0

    @pytest.mark.asyncio
    async def test_close_without_starting(self, async_client, manager):
        manager.redis_client = async_client
        await manager.close()

    @pytest.mark.asyncio
    async def test_publish_and_consume_roundtrip(self, async_client, manager):
        received = []

        @manager.on_message("roundtrip")
        async def handler(data):
            received.append(data)

        manager.redis_client = async_client
        manager.poll_interval = 0.1
        await manager.start()
        await asyncio.sleep(0.1)

        await manager.publish("roundtrip", {"roundtrip": True})
        await asyncio.sleep(1.0)

        await manager.stop()
        assert len(received) >= 1
        assert received[0] == {"roundtrip": True}
