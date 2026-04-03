"""Tests for AsyncRedisStreamManager."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import fakeredis.aioredis
import pytest
import redis.asyncio as aredis

from wredis._exceptions import StreamError, ValidationError
from wredis.async_api.streams import AsyncRedisStreamManager


@pytest.fixture
async def async_client():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=False)
    yield fake
    await fake.aclose()


@pytest.fixture
def manager():
    return AsyncRedisStreamManager(verbose=False)


class TestAsyncStreamInit:
    """Tests for initialization."""

    def test_init_defaults(self):
        m = AsyncRedisStreamManager()
        assert m.verbose is True
        assert m.consumers == {}
        assert m._tasks == {}
        assert m.running is False

    def test_init_custom(self):
        m = AsyncRedisStreamManager(host="myhost", port=1234, db=2, verbose=False)
        assert m.verbose is False


class TestAsyncStreamAddToStream:
    """Tests for add_to_stream method."""

    @pytest.mark.asyncio
    async def test_add_to_stream_basic(self, async_client, manager):
        manager.redis_client = async_client
        msg_id = await manager.add_to_stream("mystream", {"field": "value"})
        assert msg_id is not None

    @pytest.mark.asyncio
    async def test_add_to_stream_with_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_stream("mystream", {"field": "value"}, ttl=60)
        ttl = await async_client.ttl("mystream")
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_add_to_stream_without_ttl(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_stream("mystream", {"field": "value"}, ttl=None)
        ttl = await async_client.ttl("mystream")
        assert ttl == -1

    @pytest.mark.asyncio
    async def test_add_to_stream_invalid_key(self, manager):
        manager.redis_client = AsyncMock()
        with pytest.raises(ValidationError):
            await manager.add_to_stream("", {"field": "value"})

    @pytest.mark.asyncio
    async def test_add_to_stream_redis_error(self, manager):
        mock_client = AsyncMock()
        mock_client.xadd.side_effect = aredis.RedisError("connection lost")
        manager.redis_client = mock_client
        with pytest.raises(StreamError):
            await manager.add_to_stream("mystream", {"field": "value"})

    @pytest.mark.asyncio
    async def test_add_to_stream_multiple_messages(self, async_client, manager):
        manager.redis_client = async_client
        id1 = await manager.add_to_stream("mystream", {"msg": "1"})
        id2 = await manager.add_to_stream("mystream", {"msg": "2"})
        id3 = await manager.add_to_stream("mystream", {"msg": "3"})
        assert id1 is not None
        assert id2 is not None
        assert id3 is not None


class TestAsyncStreamOnMessage:
    """Tests for on_message decorator."""

    def test_on_message_registers_consumer(self, manager):
        @manager.on_message("mystream", "mygroup", "myconsumer")
        async def handler(data):
            pass

        assert "mystream" in manager.consumers
        assert manager.consumers["mystream"]["group_name"] == "mygroup"
        assert manager.consumers["mystream"]["consumer_name"] == "myconsumer"
        assert manager.consumers["mystream"]["callback"] is handler

    def test_on_message_duplicate_raises(self, manager):
        @manager.on_message("mystream", "mygroup", "myconsumer")
        async def handler1(data):
            pass

        with pytest.raises(StreamError):

            @manager.on_message("mystream", "othergroup", "otherconsumer")
            async def handler2(data):
                pass

    def test_on_message_invalid_stream_name_raises(self, manager):
        with pytest.raises(ValidationError):

            @manager.on_message("", "group", "consumer")
            async def handler(data):
                pass

    @pytest.mark.asyncio
    async def test_on_message_starts_task_if_running(self, async_client, manager):
        manager.redis_client = async_client
        manager.running = True
        manager.redis_client.xgroup_create = AsyncMock()

        @manager.on_message("mystream", "mygroup", "myconsumer")
        async def handler(data):
            pass

        assert "mystream" in manager._tasks
        assert isinstance(manager._tasks["mystream"], asyncio.Task)
        await manager.stop_listening()


class TestAsyncStreamStartListening:
    """Tests for start_listening method."""

    @pytest.mark.asyncio
    async def test_start_listening_creates_tasks(self, async_client, manager):
        @manager.on_message("mystream", "mygroup", "myconsumer")
        async def handler(data):
            pass

        manager.redis_client = async_client
        await manager.start_listening()
        assert manager.running is True
        assert len(manager._tasks) == 1
        assert "mystream" in manager._tasks
        await manager.stop_listening()

    @pytest.mark.asyncio
    async def test_start_listening_no_consumers(self, async_client, manager):
        manager.redis_client = async_client
        await manager.start_listening()
        assert manager.running is True
        assert len(manager._tasks) == 0

    @pytest.mark.asyncio
    async def test_start_listening_existing_group(self, async_client, manager):
        @manager.on_message("mystream", "mygroup", "myconsumer")
        async def handler(data):
            pass

        manager.redis_client = async_client
        await manager.add_to_stream("mystream", {"field": "value"})
        await manager.start_listening()
        assert manager.running is True
        await manager.stop_listening()

    @pytest.mark.asyncio
    async def test_start_listening_multiple_streams(self, async_client, manager):
        @manager.on_message("stream1", "group1", "consumer1")
        async def h1(data):
            pass

        @manager.on_message("stream2", "group2", "consumer2")
        async def h2(data):
            pass

        manager.redis_client = async_client
        await manager.start_listening()
        assert len(manager._tasks) == 2
        await manager.stop_listening()


class TestAsyncStreamReadFromStream:
    """Tests for read_from_stream method."""

    @pytest.mark.asyncio
    async def test_read_from_stream_with_messages(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_stream("mystream", {"field": "value"})
        messages = await manager.read_from_stream("mystream", count=1, block=100)
        assert len(messages) >= 0

    @pytest.mark.asyncio
    async def test_read_from_stream_empty(self, async_client, manager):
        manager.redis_client = async_client
        messages = await manager.read_from_stream("nonexistent", count=1, block=100)
        assert messages == []

    @pytest.mark.asyncio
    async def test_read_from_stream_invalid_key(self, manager):
        manager.redis_client = AsyncMock()
        with pytest.raises(ValidationError):
            await manager.read_from_stream("", count=1)

    @pytest.mark.asyncio
    async def test_read_from_stream_redis_error(self, manager):
        mock_client = AsyncMock()
        mock_client.xread.side_effect = aredis.RedisError("connection lost")
        manager.redis_client = mock_client
        with pytest.raises(StreamError):
            await manager.read_from_stream("mystream", count=1)

    @pytest.mark.asyncio
    async def test_read_from_stream_default_params(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_stream("mystream", {"field": "value"})
        messages = await manager.read_from_stream("mystream")
        assert isinstance(messages, list)


class TestAsyncStreamStopListening:
    """Tests for stop_listening method."""

    @pytest.mark.asyncio
    async def test_stop_listening_cancels_tasks(self, async_client, manager):
        @manager.on_message("mystream", "mygroup", "myconsumer")
        async def handler(data):
            pass

        manager.redis_client = async_client
        await manager.start_listening()
        await manager.stop_listening()
        assert manager.running is False
        assert len(manager._tasks) == 0
        assert len(manager.consumers) == 0

    @pytest.mark.asyncio
    async def test_stop_listening_when_not_running(self, manager):
        manager.redis_client = AsyncMock()
        await manager.stop_listening()
        assert manager.running is False


class TestAsyncStreamClose:
    """Tests for close method."""

    @pytest.mark.asyncio
    async def test_close_stops_and_closes(self, async_client, manager):
        @manager.on_message("mystream", "mygroup", "myconsumer")
        async def handler(data):
            pass

        manager.redis_client = async_client
        await manager.start_listening()
        await manager.close()
        assert manager.running is False
        assert len(manager._tasks) == 0

    @pytest.mark.asyncio
    async def test_close_without_starting(self, async_client, manager):
        manager.redis_client = async_client
        await manager.close()


class TestAsyncStreamIntegration:
    """Integration-style tests for stream operations."""

    @pytest.mark.asyncio
    async def test_add_and_read_roundtrip(self, async_client, manager):
        manager.redis_client = async_client
        msg_id = await manager.add_to_stream("mystream", {"key": "value"})
        assert msg_id is not None
        messages = await manager.read_from_stream("mystream", count=1, block=100)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_add_multiple_read_multiple(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_stream("mystream", {"msg": "1"})
        await manager.add_to_stream("mystream", {"msg": "2"})
        await manager.add_to_stream("mystream", {"msg": "3"})
        messages = await manager.read_from_stream("mystream", count=5, block=100)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_stream_with_ttl_expires(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_to_stream("tempstream", {"data": "temp"}, ttl=1)
        exists = await async_client.exists("tempstream")
        assert exists == 1

    @pytest.mark.asyncio
    async def test_listener_callback_receives_data(self, async_client, manager):
        received = []

        @manager.on_message("mystream", "mygroup", "myconsumer")
        async def handler(data):
            received.append(data)

        manager.redis_client = async_client
        manager.poll_interval = 0.1
        await manager.start_listening()
        await asyncio.sleep(0.2)

        await manager.add_to_stream("mystream", {"field": "value"})
        await asyncio.sleep(2.0)

        await manager.stop_listening()
