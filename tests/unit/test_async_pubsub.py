"""Tests for AsyncRedisPubSubManager."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import fakeredis.aioredis
import pytest
import redis.asyncio as aredis

from wredis._exceptions import PubSubError, ValidationError
from wredis.async_api.pubsub import AsyncRedisPubSubManager


@pytest.fixture
async def async_client():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=False)
    yield fake
    await fake.aclose()


@pytest.fixture
def manager():
    return AsyncRedisPubSubManager(verbose=False)


class TestAsyncPubSubInit:
    """Tests for initialization."""

    def test_init_defaults(self):
        m = AsyncRedisPubSubManager()
        assert m.verbose is True
        assert m.subscribers == {}
        assert m._tasks == {}
        assert m._running is False

    def test_init_custom(self):
        m = AsyncRedisPubSubManager(host="myhost", port=1234, db=2, verbose=False)
        assert m.verbose is False


class TestAsyncPubSubPublish:
    """Tests for publish_message method."""

    @pytest.mark.asyncio
    async def test_publish_string_message(self, async_client, manager):
        manager.redis_client = async_client
        await manager.publish_message("test_channel", "hello")
        await async_client.pubsub_channels()
        assert True

    @pytest.mark.asyncio
    async def test_publish_dict_message(self, async_client, manager):
        manager.redis_client = async_client
        payload = {"key": "value", "num": 42}
        await manager.publish_message("test_channel", payload)

    @pytest.mark.asyncio
    async def test_publish_invalid_channel(self, manager):
        manager.redis_client = AsyncMock()
        with pytest.raises(ValidationError):
            await manager.publish_message("", "hello")

    @pytest.mark.asyncio
    async def test_publish_invalid_message_type(self, async_client, manager):
        manager.redis_client = async_client
        with pytest.raises(ValidationError):
            await manager.publish_message("test_channel", 123)

    @pytest.mark.asyncio
    async def test_publish_redis_error(self, manager):
        mock_client = AsyncMock()
        mock_client.publish.side_effect = aredis.RedisError("connection lost")
        manager.redis_client = mock_client
        with pytest.raises(PubSubError):
            await manager.publish_message("test_channel", "hello")

    @pytest.mark.asyncio
    async def test_publish_validation_error_passthrough(self, manager):
        mock_client = AsyncMock()
        manager.redis_client = mock_client
        with pytest.raises(ValidationError):
            await manager.publish_message("", "hello")


class TestAsyncPubSubOnMessage:
    """Tests for on_message decorator."""

    def test_on_message_registers_callback(self, manager):
        @manager.on_message("test_channel")
        async def handler(data):
            pass

        assert "test_channel" in manager.subscribers
        assert manager.subscribers["test_channel"] is handler

    def test_on_message_duplicate_channel_raises(self, manager):
        @manager.on_message("test_channel")
        async def handler1(data):
            pass

        with pytest.raises(PubSubError):

            @manager.on_message("test_channel")
            async def handler2(data):
                pass

    def test_on_message_invalid_channel_raises(self, manager):
        with pytest.raises(ValidationError):

            @manager.on_message("")
            async def handler(data):
                pass

    @pytest.mark.asyncio
    async def test_on_message_starts_task_if_running(self, async_client, manager):
        manager.redis_client = async_client
        manager._running = True

        @manager.on_message("test_channel")
        async def handler(data):
            pass

        assert "test_channel" in manager._tasks
        assert isinstance(manager._tasks["test_channel"], asyncio.Task)
        await manager.stop_listening()


class TestAsyncPubSubListening:
    """Tests for start/stop listening."""

    @pytest.mark.asyncio
    async def test_start_listening_creates_tasks(self, async_client, manager):
        manager.redis_client = async_client

        @manager.on_message("ch1")
        async def h1(data):
            pass

        @manager.on_message("ch2")
        async def h2(data):
            pass

        await manager.start_listening()
        assert manager._running is True
        assert len(manager._tasks) == 2
        await manager.stop_listening()

    @pytest.mark.asyncio
    async def test_start_listening_no_subscribers(self, async_client, manager):
        manager.redis_client = async_client
        await manager.start_listening()
        assert manager._running is True
        assert len(manager._tasks) == 0

    @pytest.mark.asyncio
    async def test_stop_listening_cancels_tasks(self, async_client, manager):
        manager.redis_client = async_client

        @manager.on_message("ch1")
        async def h1(data):
            pass

        await manager.start_listening()
        await manager.stop_listening()
        assert manager._running is False
        assert len(manager._tasks) == 0
        assert len(manager.subscribers) == 0

    @pytest.mark.asyncio
    async def test_stop_listening_when_not_running(self, manager):
        manager.redis_client = AsyncMock()
        await manager.stop_listening()
        assert manager._running is False


class TestAsyncPubSubMessageDelivery:
    """Tests for actual message delivery through pub/sub."""

    @pytest.mark.asyncio
    async def test_message_delivery_to_async_callback(self, async_client, manager):
        received = []

        @manager.on_message("test_ch")
        async def handler(data):
            received.append(data)

        manager.redis_client = async_client
        await manager.start_listening()
        await asyncio.sleep(0.1)

        await async_client.publish("test_ch", "hello world")
        await asyncio.sleep(0.5)

        await manager.stop_listening()
        assert len(received) >= 1
        assert received[0] == "hello world"

    @pytest.mark.asyncio
    async def test_message_delivery_to_sync_callback(self, async_client, manager):
        received = []

        @manager.on_message("test_ch")
        def handler(data):
            received.append(data)

        manager.redis_client = async_client
        await manager.start_listening()
        await asyncio.sleep(0.1)

        await async_client.publish("test_ch", "sync message")
        await asyncio.sleep(0.5)

        await manager.stop_listening()
        assert len(received) >= 1
        assert received[0] == "sync message"

    @pytest.mark.asyncio
    async def test_message_delivery_json_deserialization(self, async_client, manager):
        received = []

        @manager.on_message("test_ch")
        async def handler(data):
            received.append(data)

        manager.redis_client = async_client
        await manager.start_listening()
        await asyncio.sleep(0.1)

        import json

        payload = json.dumps({"key": "value"})
        await async_client.publish("test_ch", payload)
        await asyncio.sleep(0.5)

        await manager.stop_listening()
        assert len(received) >= 1
        assert isinstance(received[0], dict)
        assert received[0] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_multiple_channels_delivery(self, async_client, manager):
        received_ch1 = []
        received_ch2 = []

        @manager.on_message("ch1")
        async def h1(data):
            received_ch1.append(data)

        @manager.on_message("ch2")
        async def h2(data):
            received_ch2.append(data)

        manager.redis_client = async_client
        await manager.start_listening()
        await asyncio.sleep(0.1)

        await async_client.publish("ch1", "msg1")
        await async_client.publish("ch2", "msg2")
        await asyncio.sleep(0.5)

        await manager.stop_listening()
        assert len(received_ch1) >= 1
        assert len(received_ch2) >= 1
        assert received_ch1[0] == "msg1"
        assert received_ch2[0] == "msg2"


class TestAsyncPubSubClose:
    """Tests for close method."""

    @pytest.mark.asyncio
    async def test_close_stops_listening_and_closes(self, async_client, manager):
        manager.redis_client = async_client

        @manager.on_message("ch1")
        async def h1(data):
            pass

        await manager.start_listening()
        await manager.close()
        assert manager._running is False
        assert len(manager._tasks) == 0

    @pytest.mark.asyncio
    async def test_close_without_listening(self, async_client, manager):
        manager.redis_client = async_client
        await manager.close()

    @pytest.mark.asyncio
    async def test_subscribe_and_publish_roundtrip(self, async_client, manager):
        received = []

        @manager.on_message("roundtrip")
        async def handler(data):
            received.append(data)

        manager.redis_client = async_client
        await manager.start_listening()
        await asyncio.sleep(0.1)

        await manager.publish_message("roundtrip", "roundtrip msg")
        await asyncio.sleep(0.5)

        await manager.stop_listening()
        assert len(received) >= 1
