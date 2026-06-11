"""Comprehensive tests covering uncovered branches in async_api modules."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import fakeredis.aioredis
import pytest
import redis.asyncio as aredis

from wredis._exceptions import PubSubError, QueueError, StreamError, ValidationError
from wredis.async_api.bitmap import AsyncRedisBitmapManager
from wredis.async_api.geo import AsyncRedisGeoManager
from wredis.async_api.hash import AsyncRedisHashManager
from wredis.async_api.hyperloglog import AsyncRedisHyperLogLogManager
from wredis.async_api.pipeline import AsyncRedisPipelineManager
from wredis.async_api.pubsub import AsyncRedisPubSubManager
from wredis.async_api.queue import AsyncRedisQueueManager
from wredis.async_api.sets import AsyncRedisSetManager
from wredis.async_api.sortedset import AsyncRedisSortedSetManager
from wredis.async_api.streams import AsyncRedisStreamManager

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
async def async_client():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=False)
    yield fake
    await fake.aclose()


@pytest.fixture
def bitmap_manager():
    return AsyncRedisBitmapManager(verbose=False)


@pytest.fixture
def bitmap_manager_verbose():
    return AsyncRedisBitmapManager(verbose=True)


@pytest.fixture
def geo_manager():
    return AsyncRedisGeoManager(verbose=False)


@pytest.fixture
def geo_manager_verbose():
    return AsyncRedisGeoManager(verbose=True)


@pytest.fixture
def hash_manager():
    return AsyncRedisHashManager(verbose=False)


@pytest.fixture
def hash_manager_verbose():
    return AsyncRedisHashManager(verbose=True)


@pytest.fixture
def hll_manager():
    return AsyncRedisHyperLogLogManager(verbose=False)


@pytest.fixture
def hll_manager_verbose():
    return AsyncRedisHyperLogLogManager(verbose=True)


@pytest.fixture
def pipeline_manager_verbose():
    return AsyncRedisPipelineManager(verbose=True)


@pytest.fixture
def sets_manager():
    return AsyncRedisSetManager(verbose=False)


@pytest.fixture
def sets_manager_verbose():
    return AsyncRedisSetManager(verbose=True)


@pytest.fixture
def zset_manager():
    return AsyncRedisSortedSetManager(verbose=False)


@pytest.fixture
def zset_manager_verbose():
    return AsyncRedisSortedSetManager(verbose=True)


@pytest.fixture
def queue_manager():
    return AsyncRedisQueueManager(poll_interval=0.1, verbose=False)


@pytest.fixture
def pubsub_manager():
    return AsyncRedisPubSubManager(verbose=False)


@pytest.fixture
def stream_manager():
    return AsyncRedisStreamManager(verbose=False)


# ============================================================
# Bitmap — uncovered branches (lines 45, 93-100)
# ============================================================


class TestAsyncRedisBitmapManagerUncovered:
    @pytest.mark.asyncio
    async def test_log_called_when_verbose(self, bitmap_manager_verbose):
        with patch("wredis.async_api.bitmap.logger") as mock_logger:
            await bitmap_manager_verbose.log("test message", level="info")
            mock_logger.info.assert_called_once_with("test message")

    @pytest.mark.asyncio
    async def test_log_custom_level(self, bitmap_manager_verbose):
        with patch("wredis.async_api.bitmap.logger") as mock_logger:
            await bitmap_manager_verbose.log("warning msg", level="warning")
            mock_logger.warning.assert_called_once_with("warning msg")

    @pytest.mark.asyncio
    async def test_exist_error_returns_false(self, bitmap_manager):
        mock_client = AsyncMock()
        mock_client.exists.side_effect = Exception("connection lost")
        bitmap_manager.redis_client = mock_client
        result = await bitmap_manager.exist("mykey")
        assert result is False

    @pytest.mark.asyncio
    async def test_exist_success(self, async_client, bitmap_manager):
        bitmap_manager.redis_client = async_client
        await async_client.setbit("bmap", 0, 1)
        assert await bitmap_manager.exist("bmap") is True
        assert await bitmap_manager.exist("nonexistent") is False


# ============================================================
# Geo — uncovered branches (lines 33, 52-59)
# ============================================================


class TestAsyncRedisGeoManagerUncovered:
    @pytest.mark.asyncio
    async def test_log_called_when_verbose(self, geo_manager_verbose):
        with patch("wredis.async_api.geo.logger") as mock_logger:
            await geo_manager_verbose.log("geo test", level="info")
            mock_logger.info.assert_called_once_with("geo test")

    @pytest.mark.asyncio
    async def test_log_custom_level(self, geo_manager_verbose):
        with patch("wredis.async_api.geo.logger") as mock_logger:
            await geo_manager_verbose.log("error test", level="error")
            mock_logger.error.assert_called_once_with("error test")

    @pytest.mark.asyncio
    async def test_exist_error_returns_false(self, geo_manager):
        mock_client = AsyncMock()
        mock_client.exists.side_effect = Exception("error")
        geo_manager.redis_client = mock_client
        assert await geo_manager.exist("mykey") is False


# ============================================================
# Hash — uncovered branches (lines 41, 127)
# ============================================================


class TestAsyncRedisHashManagerUncovered:
    @pytest.mark.asyncio
    async def test_log_called_when_verbose(self, hash_manager_verbose):
        with patch("wredis.async_api.hash.logger") as mock_logger:
            await hash_manager_verbose.log("hash test", level="info")
            mock_logger.info.assert_called_once_with("hash test")

    @pytest.mark.asyncio
    async def test_log_custom_level(self, hash_manager_verbose):
        with patch("wredis.async_api.hash.logger") as mock_logger:
            await hash_manager_verbose.log("error test", level="error")
            mock_logger.error.assert_called_once_with("error test")

    @pytest.mark.asyncio
    async def test_update_hash_exception_path(self, hash_manager):
        """Cover update_hash's except block when read_hash succeeds but create_hash fails."""
        mock_client = AsyncMock()
        mock_client.hget.return_value = b'{"a": 1}'
        mock_client.hset.side_effect = Exception("write error")
        hash_manager.redis_client = mock_client
        await hash_manager.update_hash("myhash", "field1", {"b": 2})
        mock_client.hset.assert_called()


# ============================================================
# HyperLogLog — uncovered branches (lines 31, 50-57)
# ============================================================


class TestAsyncRedisHyperLogLogManagerUncovered:
    @pytest.mark.asyncio
    async def test_log_called_when_verbose(self, hll_manager_verbose):
        with patch("wredis.async_api.hyperloglog.logger") as mock_logger:
            await hll_manager_verbose.log("hll test", level="info")
            mock_logger.info.assert_called_once_with("hll test")

    @pytest.mark.asyncio
    async def test_log_custom_level(self, hll_manager_verbose):
        with patch("wredis.async_api.hyperloglog.logger") as mock_logger:
            await hll_manager_verbose.log("warning msg", level="warning")
            mock_logger.warning.assert_called_once_with("warning msg")

    @pytest.mark.asyncio
    async def test_exist_error_returns_false(self, hll_manager):
        mock_client = AsyncMock()
        mock_client.exists.side_effect = Exception("error")
        hll_manager.redis_client = mock_client
        assert await hll_manager.exist("mykey") is False


# ============================================================
# Pipeline — uncovered branches (line 33)
# ============================================================


class TestAsyncRedisPipelineManagerUncovered:
    @pytest.mark.asyncio
    async def test_log_called_when_verbose(self, pipeline_manager_verbose):
        with patch("wredis.async_api.pipeline.logger") as mock_logger:
            await pipeline_manager_verbose.log("pipe test", level="info")
            mock_logger.info.assert_called_once_with("pipe test")

    @pytest.mark.asyncio
    async def test_log_custom_level(self, pipeline_manager_verbose):
        with patch("wredis.async_api.pipeline.logger") as mock_logger:
            await pipeline_manager_verbose.log("error msg", level="error")
            mock_logger.error.assert_called_once_with("error msg")


# ============================================================
# Sets — uncovered branches (lines 31, 64-71)
# ============================================================


class TestAsyncRedisSetManagerUncovered:
    @pytest.mark.asyncio
    async def test_log_called_when_verbose(self, sets_manager_verbose):
        with patch("wredis.async_api.sets.logger") as mock_logger:
            await sets_manager_verbose.log("set test", level="info")
            mock_logger.info.assert_called_once_with("set test")

    @pytest.mark.asyncio
    async def test_log_custom_level(self, sets_manager_verbose):
        with patch("wredis.async_api.sets.logger") as mock_logger:
            await sets_manager_verbose.log("warning msg", level="warning")
            mock_logger.warning.assert_called_once_with("warning msg")

    @pytest.mark.asyncio
    async def test_exist_error_returns_false(self, sets_manager):
        mock_client = AsyncMock()
        mock_client.exists.side_effect = Exception("error")
        sets_manager.redis_client = mock_client
        assert await sets_manager.exist("mykey") is False

    @pytest.mark.asyncio
    async def test_exist_success(self, async_client, sets_manager):
        sets_manager.redis_client = async_client
        await async_client.sadd("myset", "a")
        assert await sets_manager.exist("myset") is True
        assert await sets_manager.exist("nonexistent") is False


# ============================================================
# SortedSet — uncovered branches (lines 31, 54-61)
# ============================================================


class TestAsyncRedisSortedSetManagerUncovered:
    @pytest.mark.asyncio
    async def test_log_called_when_verbose(self, zset_manager_verbose):
        with patch("wredis.async_api.sortedset.logger") as mock_logger:
            await zset_manager_verbose.log("zset test", level="info")
            mock_logger.info.assert_called_once_with("zset test")

    @pytest.mark.asyncio
    async def test_log_custom_level(self, zset_manager_verbose):
        with patch("wredis.async_api.sortedset.logger") as mock_logger:
            await zset_manager_verbose.log("error msg", level="error")
            mock_logger.error.assert_called_once_with("error msg")

    @pytest.mark.asyncio
    async def test_exist_error_returns_false(self, zset_manager):
        mock_client = AsyncMock()
        mock_client.exists.side_effect = Exception("error")
        zset_manager.redis_client = mock_client
        assert await zset_manager.exist("mykey") is False

    @pytest.mark.asyncio
    async def test_exist_success(self, async_client, zset_manager):
        zset_manager.redis_client = async_client
        await async_client.zadd("myzset", {"a": 1.0})
        assert await zset_manager.exist("myzset") is True
        assert await zset_manager.exist("nonexistent") is False


# ============================================================
# Queue — uncovered branches (lines 90->exit, 102-106, 108-112,
#                             148->151, 178)
# ============================================================


class TestAsyncRedisQueueManagerUncovered:
    @pytest.mark.asyncio
    async def test_publish_re_raises_validation_error(self, queue_manager):
        """Cover `except (ValidationError, QueueError): raise` in publish (line 178)."""
        mock_client = AsyncMock()
        mock_client.rpush.side_effect = ValidationError("test")
        queue_manager.redis_client = mock_client
        with pytest.raises(ValidationError):
            await queue_manager.publish("valid_queue", {"key": "value"})

    @pytest.mark.asyncio
    async def test_consume_json_decode_error_breaks(self, queue_manager):
        """Cover JSONDecodeError + retry + break in _consume_queue (lines 102-106)."""
        calls = []

        @queue_manager.on_message("test_queue")
        async def handler(data):
            calls.append(data)

        mock_client = AsyncMock()
        mock_client.brpop.return_value = ("test_queue", b"invalid json{{{")
        mock_client.rpush = AsyncMock()
        mock_client.expire = AsyncMock()
        queue_manager.redis_client = mock_client
        queue_manager.max_retries = 1

        await queue_manager.start()
        await asyncio.sleep(0.5)
        await queue_manager.stop()

        assert queue_manager.running is False
        assert len(queue_manager._tasks) == 0

    @pytest.mark.asyncio
    async def test_consume_redis_error_breaks(self, queue_manager):
        """Cover RedisError + retry + break in _consume_queue (lines 108-112)."""
        calls = []

        @queue_manager.on_message("test_queue")
        async def handler(data):
            calls.append(data)

        mock_client = AsyncMock()
        mock_client.brpop.side_effect = aredis.RedisError("timeout")
        mock_client.rpush = AsyncMock()
        mock_client.expire = AsyncMock()
        queue_manager.redis_client = mock_client
        queue_manager.max_retries = 1

        await queue_manager.start()
        await asyncio.sleep(0.5)
        await queue_manager.stop()

        assert queue_manager.running is False
        assert len(queue_manager._tasks) == 0

    @pytest.mark.asyncio
    async def test_stop_with_tasks_gathers(self, queue_manager):
        """Cover `if self._tasks: await asyncio.gather(...)` in stop (lines 148->151)."""

        @queue_manager.on_message("test_queue")
        async def handler(data):
            pass

        mock_client = AsyncMock()
        mock_client.brpop.return_value = None
        queue_manager.redis_client = mock_client

        await queue_manager.start()
        assert len(queue_manager._tasks) == 1
        await queue_manager.stop()
        assert queue_manager.running is False
        assert len(queue_manager._tasks) == 0


# ============================================================
# PubSub — uncovered branches (lines 133->155, 137->139,
#                               145-146, 152-153)
# ============================================================


class TestAsyncRedisPubSubManagerUncovered:
    @pytest.mark.asyncio
    async def test_message_delivery_bytes_decode(self, async_client, pubsub_manager):
        """Cover bytes decode path in _listen_channel (lines 137->139)."""
        received = []

        @pubsub_manager.on_message("test_ch")
        async def handler(data):
            received.append(data)

        pubsub_manager.redis_client = async_client
        await pubsub_manager.start_listening()
        await asyncio.sleep(0.1)

        await async_client.publish("test_ch", "hello bytes")
        await asyncio.sleep(0.5)

        await pubsub_manager.stop_listening()
        assert len(received) >= 1
        assert received[0] == "hello bytes"

    @pytest.mark.asyncio
    async def test_error_processing_in_listener(self):
        """Cover the async for loop error processing (lines 145-146)."""
        mgr = AsyncRedisPubSubManager(verbose=False)

        @mgr.on_message("test_ch")
        async def handler(data):
            raise RuntimeError("handler failure")

        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()

        async def mock_listen():
            yield {"type": "message", "data": "hello", "channel": b"test_ch"}
            yield {"type": "message", "data": "world", "channel": b"test_ch"}

        mock_pubsub.listen = mock_listen

        mock_client = AsyncMock()
        mock_client.pubsub.return_value = mock_pubsub
        mgr.redis_client = mock_client

        await mgr.start_listening()
        await asyncio.sleep(0.2)
        await mgr.stop_listening()

        assert mgr._running is False

    @pytest.mark.asyncio
    async def test_redis_error_in_listener(self):
        """Cover RedisError caught in _listen_channel (lines 152-153)."""
        mgr = AsyncRedisPubSubManager(verbose=False)

        @mgr.on_message("test_ch")
        async def handler(data):
            pass

        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()

        async def mock_listen():
            yield {"type": "message", "data": "hello", "channel": b"test_ch"}
            raise aredis.RedisError("connection lost")

        mock_pubsub.listen = mock_listen

        mock_client = AsyncMock()
        mock_client.pubsub.return_value = mock_pubsub
        mgr.redis_client = mock_client

        await mgr.start_listening()
        await asyncio.sleep(0.2)
        await mgr.stop_listening()

        assert mgr._running is False


# ============================================================
# Streams — uncovered branches (lines 75, 124-125, 147->exit,
#                                157-167, 169-170, 172, 174, 220)
# ============================================================


class TestAsyncRedisStreamManagerUncovered:
    @pytest.mark.asyncio
    async def test_add_to_stream_re_raises_validation_error(self):
        """Cover `except (ValidationError, StreamError): raise` in add_to_stream (line 75)."""
        mgr = AsyncRedisStreamManager(verbose=False)
        mock_client = AsyncMock()
        mock_client.xadd.side_effect = ValidationError("test")
        mgr.redis_client = mock_client
        with pytest.raises(ValidationError):
            await mgr.add_to_stream("valid_key", {"field": "value"})

    @pytest.mark.asyncio
    async def test_read_from_stream_re_raises_validation_error(self):
        """Cover `except (ValidationError, StreamError): raise` in read_from_stream (line 220)."""
        mgr = AsyncRedisStreamManager(verbose=False)
        mock_client = AsyncMock()
        mock_client.xread.side_effect = ValidationError("test")
        mgr.redis_client = mock_client
        with pytest.raises(ValidationError):
            await mgr.read_from_stream("valid_key", count=1)

    @pytest.mark.asyncio
    async def test_listener_processes_message(self):
        """Cover message processing in _listen_stream (lines 157-167)."""
        mgr = AsyncRedisStreamManager(verbose=False)

        mock_client = AsyncMock()
        mock_client.xgroup_create = AsyncMock()
        mock_client.xack = AsyncMock()

        call_count = 0

        async def mock_xreadgroup(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0)
            if call_count == 2:
                return [[b"mystream", [(b"msg-id", {b"field": b"value"})]]]
            return []

        mock_client.xreadgroup = mock_xreadgroup
        mgr.redis_client = mock_client

        received = []

        @mgr.on_message("mystream", "mygroup", "myconsumer")
        async def handler(data):
            received.append(data)

        await mgr.start_listening()
        await asyncio.sleep(0.3)
        await mgr.stop_listening()

        assert len(received) >= 1
        assert received[0] == {"field": "value"}
        mock_client.xack.assert_called_once()

    @pytest.mark.asyncio
    async def test_listener_sync_callback(self):
        """Cover sync callback path in _listen_stream (line 166)."""
        mgr = AsyncRedisStreamManager(verbose=False)

        mock_client = AsyncMock()
        mock_client.xgroup_create = AsyncMock()
        mock_client.xack = AsyncMock()

        call_count = 0

        async def mock_xreadgroup(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0)
            if call_count == 2:
                return [[b"mystream", [(b"msg-id", {b"field": b"value"})]]]
            return []

        mock_client.xreadgroup = mock_xreadgroup
        mgr.redis_client = mock_client

        received = []

        @mgr.on_message("mystream", "mygroup", "myconsumer")
        def handler(data):
            received.append(data)

        await mgr.start_listening()
        await asyncio.sleep(0.3)
        await mgr.stop_listening()

        assert len(received) >= 1
        assert received[0] == {"field": "value"}
        mock_client.xack.assert_called_once()

    @pytest.mark.asyncio
    async def test_listener_redis_error_handling(self):
        """Cover RedisError handler in _listen_stream (lines 169-170)."""
        mgr = AsyncRedisStreamManager(verbose=False)

        @mgr.on_message("mystream", "mygroup", "myconsumer")
        async def handler(data):
            pass

        mock_client = AsyncMock()
        mock_client.xgroup_create = AsyncMock()

        call_count = 0

        async def mock_xreadgroup(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0)
            if call_count >= 2:
                return []
            raise aredis.RedisError("timeout")

        mock_client.xreadgroup = mock_xreadgroup
        mgr.redis_client = mock_client

        await mgr.start_listening()
        await asyncio.sleep(1.2)
        await mgr.stop_listening()

        assert mgr.running is False

    @pytest.mark.asyncio
    async def test_listener_unexpected_error_handling(self):
        """Cover generic Exception handler in _listen_stream (line 174)."""
        mgr = AsyncRedisStreamManager(verbose=False)

        @mgr.on_message("mystream", "mygroup", "myconsumer")
        async def handler(data):
            pass

        mock_client = AsyncMock()
        mock_client.xgroup_create = AsyncMock()

        async def mock_xreadgroup(*args, **kwargs):
            await asyncio.sleep(0)
            raise RuntimeError("unexpected")

        mock_client.xreadgroup = mock_xreadgroup
        mgr.redis_client = mock_client

        await mgr.start_listening()
        await asyncio.sleep(0.3)
        await mgr.stop_listening()

        assert mgr.running is False
