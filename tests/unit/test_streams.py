"""Tests for wredis.streams.RedisStreamManager."""

import time
from unittest.mock import MagicMock, patch

import fakeredis
import pytest
import redis

from wredis._exceptions import StreamError, ValidationError
from wredis.streams.streams import RedisStreamManager


@pytest.fixture
def stream_manager():
    """Provide a RedisStreamManager backed by fakeredis."""
    fake = fakeredis.FakeRedis(decode_responses=False)
    manager = RedisStreamManager(host="localhost", port=6379, db=0, verbose=False)
    manager.redis_client = fake
    yield manager
    fake.flushall()
    manager.running = False


class TestRedisStreamManagerAddToStream:
    """Test add_to_stream method."""

    def test_add_to_stream_success(self, stream_manager):
        """Test adding a message to a stream."""
        msg_id = stream_manager.add_to_stream("mystream", {"field": "value"})

        assert msg_id is not None
        messages = stream_manager.redis_client.xrange("mystream")
        assert len(messages) == 1
        assert messages[0][1] == {b"field": b"value"}

    def test_add_to_stream_with_ttl(self, stream_manager):
        """Test adding a message with TTL."""
        msg_id = stream_manager.add_to_stream("mystream", {"field": "value"}, ttl=60)

        assert msg_id is not None
        ttl = stream_manager.redis_client.ttl("mystream")
        assert ttl > 0

    def test_add_to_stream_invalid_key(self, stream_manager):
        """Test add_to_stream raises ValidationError for empty key."""
        with pytest.raises(ValidationError, match="Redis key cannot be empty"):
            stream_manager.add_to_stream("", {"field": "value"})

    def test_add_to_stream_key_too_long(self, stream_manager):
        """Test add_to_stream raises ValidationError for long key."""
        long_key = "k" * 600
        with pytest.raises(ValidationError, match="Redis key too long"):
            stream_manager.add_to_stream(long_key, {"field": "value"})

    def test_add_to_stream_redis_error(self, stream_manager):
        """Test add_to_stream raises StreamError on Redis failure."""
        original_xadd = stream_manager.redis_client.xadd
        stream_manager.redis_client.xadd = MagicMock(side_effect=redis.RedisError("Redis error"))

        with pytest.raises(StreamError, match="Failed to add to stream"):
            stream_manager.add_to_stream("mystream", {"field": "value"})

        stream_manager.redis_client.xadd = original_xadd


class TestRedisStreamManagerOnMessage:
    """Test on_message decorator."""

    def test_on_message_registers_consumer(self, stream_manager):
        """Test on_message registers a consumer."""

        @stream_manager.on_message("mystream", "mygroup", "consumer1")
        def handler(data):
            pass

        assert "mystream" in stream_manager.consumers
        assert stream_manager.consumers["mystream"]["group_name"] == "mygroup"
        assert stream_manager.consumers["mystream"]["consumer_name"] == "consumer1"
        assert stream_manager.consumers["mystream"]["callback"] is handler

    def test_on_message_invalid_key(self, stream_manager):
        """Test on_message raises ValidationError for empty key."""
        with pytest.raises(ValidationError, match="Redis key cannot be empty"):

            @stream_manager.on_message("", "group", "consumer")
            def handler(data):
                pass

    def test_on_message_duplicate_registration(self, stream_manager):
        """Test on_message raises StreamError for duplicate registration."""

        @stream_manager.on_message("mystream", "mygroup", "consumer1")
        def handler(data):
            pass

        with pytest.raises(StreamError, match="Consumer already registered"):

            @stream_manager.on_message("mystream", "mygroup2", "consumer2")
            def handler2(data):
                pass


class TestRedisStreamManagerDecodeMessage:
    """Test _decode_message method."""

    def test_decode_message_bytes(self, stream_manager):
        """Test decoding bytes message data."""
        raw = {b"key1": b"value1", b"key2": b"value2"}
        decoded = stream_manager._decode_message(raw)

        assert decoded == {"key1": "value1", "key2": "value2"}

    def test_decode_message_mixed(self, stream_manager):
        """Test decoding mixed bytes and non-bytes values."""
        raw = {b"key1": "already_string"}
        decoded = stream_manager._decode_message(raw)

        assert decoded == {"key1": "already_string"}


class TestRedisStreamManagerReadFromStream:
    """Test read_from_stream method."""

    def test_read_from_stream_with_block(self, stream_manager):
        """Test reading from a stream with blocking."""
        stream_manager.add_to_stream("mystream", {"field": "value"})

        messages = stream_manager.redis_client.xread({"mystream": "0"}, count=1, block=0)

        assert messages is not None
        assert len(messages) == 1
        assert messages[0][0] == b"mystream"
        assert len(messages[0][1]) == 1

    def test_read_from_stream_empty(self, stream_manager):
        """Test reading from an empty stream with xrange."""
        messages = stream_manager.redis_client.xrange("mystream")

        assert messages == []

    def test_read_from_stream_invalid_key(self, stream_manager):
        """Test read_from_stream raises ValidationError for empty key."""
        with pytest.raises(ValidationError, match="Redis key cannot be empty"):
            stream_manager.read_from_stream("", count=1)

    def test_read_from_stream_redis_error(self, stream_manager):
        """Test read_from_stream raises StreamError on Redis failure."""
        original_xread = stream_manager.redis_client.xread
        stream_manager.redis_client.xread = MagicMock(side_effect=redis.RedisError("Redis error"))

        with pytest.raises(StreamError, match="Failed to read from stream"):
            stream_manager.read_from_stream("mystream", count=1)

        stream_manager.redis_client.xread = original_xread


class TestRedisStreamManagerStopConsumers:
    """Test stop_consumers method."""

    def test_stop_consumers(self, stream_manager):
        """Test stop_consumers clears state."""
        stream_manager.running = True
        stream_manager.consumers["mystream"] = {"callback": lambda x: None}

        stream_manager.stop_consumers()

        assert stream_manager.running is False
        assert len(stream_manager.consumers) == 0


class TestRedisStreamManagerStartListener:
    """Test _start_listener method."""

    def test_start_listener_creates_group(self, stream_manager):
        """Test _start_listener creates consumer group."""
        stream_manager.redis_client.xadd("mystream", {"field": "value"})

        @stream_manager.on_message("mystream", "mygroup", "consumer1")
        def handler(data):
            pass

        time.sleep(0.2)

        groups = stream_manager.redis_client.xinfo_groups("mystream")
        assert len(groups) == 1
        assert groups[0]["name"] == b"mygroup"

    def test_start_listener_existing_group(self, stream_manager):
        """Test _start_listener handles existing group gracefully."""
        stream_manager.redis_client.xadd("mystream", {"field": "value"})
        stream_manager.redis_client.xgroup_create("mystream", "mygroup", id="0", mkstream=True)

        @stream_manager.on_message("mystream", "mygroup", "consumer1")
        def handler(data):
            pass

        time.sleep(0.2)
        assert stream_manager.running is True


class TestStreamIntegration:
    """Integration tests for stream operations."""

    def test_add_and_read_message(self, stream_manager):
        """Test adding and reading a message from a stream."""
        stream_manager.add_to_stream("teststream", {"key": "value", "num": "42"})

        messages = stream_manager.redis_client.xrange("teststream")

        assert len(messages) == 1
        assert messages[0][1] == {b"key": b"value", b"num": b"42"}

    def test_multiple_messages(self, stream_manager):
        """Test adding multiple messages to a stream."""
        stream_manager.add_to_stream("teststream", {"msg": "1"})
        stream_manager.add_to_stream("teststream", {"msg": "2"})
        stream_manager.add_to_stream("teststream", {"msg": "3"})

        messages = stream_manager.redis_client.xrange("teststream")

        assert len(messages) == 3

    def test_consumer_callback_receives_message(self, stream_manager):
        """Test that consumer callback receives decoded messages."""
        received = []

        stream_manager.redis_client.xadd("teststream", {"data": "hello"})
        stream_manager.redis_client.xgroup_create("teststream", "testgroup", id="0", mkstream=True)

        @stream_manager.on_message("teststream", "testgroup", "testconsumer")
        def handler(data):
            received.append(data)

        time.sleep(1.5)

        assert len(received) == 1
        assert received[0] == {"data": "hello"}
