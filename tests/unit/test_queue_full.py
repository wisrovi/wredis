"""Extended coverage tests for wredis.queue.RedisQueueManager.

Targets missing lines:
- queue.py: 98-99, 137->136, 166, 195-200
"""

import json
import signal
import threading
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


class TestConsumeQueueJsonMaxRetries:
    """Target lines 98-99: max retries on JSONDecodeError."""

    def test_consume_queue_json_decode_max_retries_breaks(self, queue_manager):
        """Test consumer breaks after max_retries JSONDecodeError occurrences."""
        received = []

        def handler(data):
            received.append(data)

        queue_manager.running = True
        queue_manager.max_retries = 2
        queue_manager.poll_interval = 0

        call_count = [0]

        def mock_brpop(queue_name, timeout=None):
            call_count[0] += 1
            raise json.JSONDecodeError("Expecting value", "doc", 0)

        queue_manager.redis_client.brpop = mock_brpop
        queue_manager._consume_queue("badqueue", handler)

        assert call_count[0] == 2
        assert len(received) == 0

    def test_consume_queue_json_decode_retries_reset_on_success(self, queue_manager):
        """Test retries reset after a successful message."""
        received = []

        def handler(data):
            received.append(data)

        queue_manager.running = True
        queue_manager.max_retries = 2
        queue_manager.poll_interval = 0

        call_order = [
            (b"q", b"not-json"),
            (b"q", json.dumps({"ok": True}).encode()),
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
        queue_manager._consume_queue("q", handler)

        assert len(received) == 1
        assert received[0] == {"ok": True}

    def test_consume_queue_single_json_error_does_not_break(self, queue_manager):
        """Test one JSON error does not break consumer."""
        received = []

        def handler(data):
            received.append(data)

        queue_manager.running = True
        queue_manager.max_retries = 3
        queue_manager.poll_interval = 0

        call_order = [
            (b"q", b"bad"),
            (b"q", json.dumps({"a": 1}).encode()),
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
        queue_manager._consume_queue("q", handler)

        assert len(received) == 1


class TestStopWithDeadThread:
    """Target line 137->136: thread.is_alive() == False branch."""

    def test_stop_skips_dead_thread(self, queue_manager):
        """Test stop() skips joining threads that are not alive."""

        @queue_manager.on_message("q1")
        def handler(data):
            pass

        queue_manager.start()
        time.sleep(0.1)
        queue_manager.stop()

        assert queue_manager.running is False
        assert len(queue_manager._threads) == 0

    def test_stop_with_manually_created_dead_thread(self, queue_manager):
        """Test stop() handles a manually added dead thread."""
        queue_manager.running = True
        dead_thread = threading.Thread(target=lambda: None, daemon=True)
        dead_thread.start()
        dead_thread.join()
        queue_manager._threads.append(dead_thread)

        queue_manager.stop()

        assert queue_manager.running is False
        assert len(queue_manager._threads) == 0


class TestPublishValidationError:
    """Target line 166: re-raise ValidationError/QueueError in publish."""

    def test_publish_re_raises_validation_error(self, queue_manager):
        """Test publish re-raises ValidationError from validate_key."""
        with pytest.raises(ValidationError, match="Redis key cannot be empty"):
            queue_manager.publish("", {"key": "value"})

    def test_publish_re_raises_validation_error_for_long_key(self, queue_manager):
        """Test publish re-raises ValidationError for too-long key."""
        long_key = "q" * 600
        with pytest.raises(ValidationError, match="Redis key too long"):
            queue_manager.publish(long_key, {"key": "value"})

    def test_publish_re_raises_validation_error_for_invalid_ttl(self, queue_manager):
        """Test publish re-raises ValidationError for invalid TTL."""
        with pytest.raises(ValidationError, match="TTL must be"):
            queue_manager.publish("myqueue", {"key": "value"}, ttl=-10)


class TestWait:
    """Target lines 195-200: wait() method with signal handler."""

    @patch("signal.signal")
    @patch("signal.pause")
    def test_wait_registers_sigint_handler(self, mock_pause, mock_signal, queue_manager):
        """Test wait() registers a SIGINT handler and calls signal.pause()."""
        queue_manager.running = True

        @queue_manager.on_message("q1")
        def handler(data):
            pass

        queue_manager.start()
        queue_manager.wait()

        mock_signal.assert_called_once()
        call_args = mock_signal.call_args
        assert call_args[0][0] == signal.SIGINT
        mock_pause.assert_called_once()

    @patch("signal.signal")
    @patch("signal.pause")
    def test_wait_signal_handler_calls_stop(self, mock_pause, mock_signal, queue_manager):
        """Test the SIGINT handler inside wait() calls stop()."""

        @queue_manager.on_message("q1")
        def handler(data):
            pass

        queue_manager.start()

        def capture_handler(sig, handler_func):
            handler_func(sig, None)

        mock_signal.side_effect = capture_handler

        with patch.object(queue_manager, "stop", wraps=queue_manager.stop) as mock_stop:
            queue_manager.wait()
            mock_stop.assert_called_once()

    @patch("signal.signal")
    @patch("signal.pause")
    def test_wait_without_callbacks_still_registers_signal(self, mock_pause, mock_signal, queue_manager):
        """Test wait() registers signal handler even without callbacks (start is called internally)."""
        queue_manager.wait()

        mock_signal.assert_called_once()
        call_args = mock_signal.call_args
        assert call_args[0][0] == signal.SIGINT
        mock_pause.assert_called_once()
