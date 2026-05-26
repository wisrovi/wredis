"""Tests for wredis.queue.RedisQueueManager."""

import json
import time
from unittest.mock import MagicMock, patch

import fakeredis
import pytest
import redis

from wredis._exceptions import QueueError, ValidationError
from wredis.queue.queue import RedisQueueManager


@pytest.fixture
def queue_manager():
    """Provide a RedisQueueManager backed by fakeredis."""
    fake = fakeredis.FakeRedis(decode_responses=False)
    manager = RedisQueueManager(
        host="localhost",
        port=6379,
        db=0,
        poll_interval=1,
        max_retries=3,
        verbose=False,
    )
    manager.redis_client = fake
    yield manager
    fake.flushall()
    manager.running = False


class TestRedisQueueManagerOnMessage:
    """Test on_message decorator."""

    def test_on_message_registers_callback(self, queue_manager):
        """Test on_message registers a callback for a queue."""

        @queue_manager.on_message("myqueue")
        def handler(data):
            pass

        assert "myqueue" in queue_manager.callbacks
        assert queue_manager.callbacks["myqueue"] is handler

    def test_on_message_invalid_key(self, queue_manager):
        """Test on_message raises ValidationError for empty key."""
        with pytest.raises(ValidationError, match="Redis key cannot be empty"):

            @queue_manager.on_message("")
            def handler(data):
                pass

    def test_on_message_key_too_long(self, queue_manager):
        """Test on_message raises ValidationError for long key."""
        long_key = "q" * 600
        with pytest.raises(ValidationError, match="Redis key too long"):

            @queue_manager.on_message(long_key)
            def handler(data):
                pass

    def test_on_message_duplicate_registration(self, queue_manager):
        """Test on_message raises QueueError for duplicate registration."""

        @queue_manager.on_message("myqueue")
        def handler(data):
            pass

        with pytest.raises(QueueError, match="Callback already registered"):

            @queue_manager.on_message("myqueue")
            def handler2(data):
                pass


class TestRedisQueueManagerPublish:
    """Test publish method."""

    def test_publish_success(self, queue_manager):
        """Test publishing a message to a queue."""
        queue_manager.publish("myqueue", {"key": "value"})

        length = queue_manager.redis_client.llen("myqueue")
        assert length == 1
        item = queue_manager.redis_client.lpop("myqueue")
        assert json.loads(item) == {"key": "value"}

    def test_publish_with_ttl(self, queue_manager):
        """Test publishing a message with TTL."""
        queue_manager.publish("myqueue", {"key": "value"}, ttl=60)

        ttl = queue_manager.redis_client.ttl("myqueue")
        assert ttl > 0

    def test_publish_invalid_key(self, queue_manager):
        """Test publish raises ValidationError for empty key."""
        with pytest.raises(ValidationError, match="Redis key cannot be empty"):
            queue_manager.publish("", {"key": "value"})

    def test_publish_invalid_ttl(self, queue_manager):
        """Test publish raises ValidationError for invalid TTL."""
        with pytest.raises(ValidationError, match="TTL must be -1"):
            queue_manager.publish("myqueue", {"key": "value"}, ttl=-5)

    @patch.object(fakeredis.FakeRedis, "rpush")
    def test_publish_redis_error(self, mock_rpush, queue_manager):
        """Test publish raises QueueError on Redis failure."""
        mock_rpush.side_effect = Exception("Redis error")

        with pytest.raises(QueueError, match="Failed to publish to queue"):
            queue_manager.publish("myqueue", {"key": "value"})


class TestRedisQueueManagerGetQueueLength:
    """Test get_queue_length method."""

    def test_get_queue_length_empty(self, queue_manager):
        """Test get_queue_length returns 0 for empty queue."""
        length = queue_manager.get_queue_length("myqueue")

        assert length == 0

    def test_get_queue_length_with_items(self, queue_manager):
        """Test get_queue_length returns correct count."""
        queue_manager.publish("myqueue", {"msg": "1"})
        queue_manager.publish("myqueue", {"msg": "2"})
        queue_manager.publish("myqueue", {"msg": "3"})

        length = queue_manager.get_queue_length("myqueue")

        assert length == 3

    def test_get_queue_length_invalid_key(self, queue_manager):
        """Test get_queue_length raises ValidationError for empty key."""
        with pytest.raises(ValidationError, match="Redis key cannot be empty"):
            queue_manager.get_queue_length("")

    def test_get_queue_length_redis_error(self, queue_manager):
        """Test get_queue_length raises QueueError on Redis failure."""
        original_llen = queue_manager.redis_client.llen
        queue_manager.redis_client.llen = MagicMock(
            side_effect=redis.RedisError("Redis error")
        )

        with pytest.raises(QueueError, match="Failed to get length of queue"):
            queue_manager.get_queue_length("myqueue")

        queue_manager.redis_client.llen = original_llen


class TestRedisQueueManagerStart:
    """Test start method."""

    def test_start_without_callbacks(self, queue_manager):
        """Test start raises QueueError when no callbacks registered."""
        with pytest.raises(QueueError, match="No callbacks registered"):
            queue_manager.start()

    def test_start_with_callbacks(self, queue_manager):
        """Test start creates consumer threads."""

        @queue_manager.on_message("myqueue")
        def handler(data):
            pass

        queue_manager.start()

        assert queue_manager.running is True
        assert len(queue_manager._threads) == 1
        assert queue_manager._threads[0].is_alive()

    def test_start_already_running(self, queue_manager):
        """Test start does nothing if already running."""

        @queue_manager.on_message("myqueue")
        def handler(data):
            pass

        queue_manager.start()
        queue_manager.start()

        assert queue_manager.running is True


class TestRedisQueueManagerStop:
    """Test stop method."""

    def test_stop(self, queue_manager):
        """Test stop sets running to False and joins threads."""

        @queue_manager.on_message("myqueue")
        def handler(data):
            pass

        queue_manager.start()
        queue_manager.stop()

        assert queue_manager.running is False
        assert len(queue_manager._threads) == 0

    def test_stop_already_stopped(self, queue_manager):
        """Test stop does nothing if already stopped."""
        queue_manager.stop()

        assert queue_manager.running is False


class TestRedisQueueManagerConsumeQueue:
    """Test _consume_queue method."""

    def test_consume_queue_processes_messages(self, queue_manager):
        """Test that _consume_queue processes messages and calls callback."""
        received = []

        def handler(data):
            received.append(data)

        queue_manager.redis_client.rpush("myqueue", json.dumps({"msg": "hello"}))
        queue_manager.redis_client.rpush("myqueue", json.dumps({"msg": "world"}))

        queue_manager.running = True
        queue_manager.poll_interval = 0

        call_order = [
            (b"myqueue", json.dumps({"msg": "hello"}).encode()),
            (b"myqueue", json.dumps({"msg": "world"}).encode()),
        ]
        call_idx = [0]

        def mock_brpop(queue_name, timeout=None):
            if call_idx[0] < len(call_order):
                result = call_order[call_idx[0]]
                call_idx[0] += 1
                return result
            queue_manager.running = False
            return None

        queue_manager.redis_client.brpop = mock_brpop

        queue_manager._consume_queue("myqueue", handler)

        assert len(received) == 2
        assert received[0] == {"msg": "hello"}
        assert received[1] == {"msg": "world"}

    def test_consume_queue_handles_invalid_json(self, queue_manager):
        """Test _consume_queue handles invalid JSON gracefully."""
        received = []

        def handler(data):
            received.append(data)

        queue_manager.redis_client.rpush("myqueue", "not-json")
        queue_manager.redis_client.rpush("myqueue", json.dumps({"msg": "valid"}))

        queue_manager.running = True
        queue_manager.poll_interval = 0

        call_order = [
            (b"myqueue", b"not-json"),
            (b"myqueue", json.dumps({"msg": "valid"}).encode()),
        ]
        call_idx = [0]

        def mock_brpop(queue_name, timeout=None):
            if call_idx[0] < len(call_order):
                result = call_order[call_idx[0]]
                call_idx[0] += 1
                return result
            queue_manager.running = False
            return None

        queue_manager.redis_client.brpop = mock_brpop

        queue_manager._consume_queue("myqueue", handler)

        assert len(received) == 1
        assert received[0] == {"msg": "valid"}

    def test_consume_queue_stops_on_max_retries(self, queue_manager):
        """Test _consume_queue stops after max retries on errors."""
        received = []

        def handler(data):
            received.append(data)

        queue_manager.running = True
        queue_manager.poll_interval = 0
        queue_manager.max_retries = 2

        call_count = [0]

        def mock_brpop(queue_name, timeout=None):
            call_count[0] += 1
            raise redis.RedisError("Connection lost")

        queue_manager.redis_client.brpop = mock_brpop

        queue_manager._consume_queue("myqueue", handler)

        assert call_count[0] == 2
        assert len(received) == 0


class TestQueueIntegration:
    """Integration tests for queue operations."""

    def test_publish_and_consume(self, queue_manager):
        """Test full publish-consume cycle."""
        received = []

        @queue_manager.on_message("testqueue")
        def handler(data):
            received.append(data)

        queue_manager.publish("testqueue", {"action": "test"})
        queue_manager.publish("testqueue", {"action": "done"})

        queue_manager.running = True
        queue_manager.poll_interval = 0

        call_order = [
            (b"testqueue", json.dumps({"action": "test"}).encode()),
            (b"testqueue", json.dumps({"action": "done"}).encode()),
        ]
        call_idx = [0]

        def mock_brpop(queue_name, timeout=None):
            if call_idx[0] < len(call_order):
                result = call_order[call_idx[0]]
                call_idx[0] += 1
                return result
            queue_manager.running = False
            return None

        queue_manager.redis_client.brpop = mock_brpop

        queue_manager._consume_queue("testqueue", handler)

        assert len(received) == 2
        assert received[0] == {"action": "test"}
        assert received[1] == {"action": "done"}

    def test_multiple_queues(self, queue_manager):
        """Test consuming from multiple queues."""
        received_a = []
        received_b = []

        @queue_manager.on_message("queue_a")
        def handler_a(data):
            received_a.append(data)

        @queue_manager.on_message("queue_b")
        def handler_b(data):
            received_b.append(data)

        queue_manager.publish("queue_a", {"from": "a"})
        queue_manager.publish("queue_b", {"from": "b"})

        queue_manager.start()
        time.sleep(0.5)
        queue_manager.stop()

        assert len(received_a) == 1
        assert len(received_b) == 1
        assert received_a[0] == {"from": "a"}
        assert received_b[0] == {"from": "b"}

    def test_queue_with_ttl(self, queue_manager):
        """Test that queue TTL is set correctly."""
        queue_manager.publish("myqueue", {"msg": "test"}, ttl=30)

        ttl = queue_manager.redis_client.ttl("myqueue")
        assert 0 < ttl <= 30
