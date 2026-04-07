"""Extended coverage tests for wredis.streams.RedisStreamManager.

Targets missing lines:
- streams.py: 70, 167-168, 176-177, 198-216, 218, 231-236
"""

import signal
import threading
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


class TestAddToStreamValidationError:
    """Target line 70: re-raise ValidationError/StreamError in add_to_stream."""

    def test_add_to_stream_re_raises_validation_error_empty_key(self, stream_manager):
        """Test add_to_stream re-raises ValidationError for empty key."""
        with pytest.raises(ValidationError, match="Redis key cannot be empty"):
            stream_manager.add_to_stream("", {"field": "value"})

    def test_add_to_stream_re_raises_validation_error_long_key(self, stream_manager):
        """Test add_to_stream re-raises ValidationError for too-long key."""
        long_key = "k" * 600
        with pytest.raises(ValidationError, match="Redis key too long"):
            stream_manager.add_to_stream(long_key, {"field": "value"})


class TestListenerGenericException:
    """Target lines 167-168: generic Exception handler in listener."""

    def test_listener_handles_generic_exception(self, stream_manager):
        """Test listener catches and logs generic exceptions."""
        stream_manager.consumers["mystream"] = {
            "group_name": "mygroup",
            "consumer_name": "consumer1",
            "callback": lambda x: None,
        }

        stream_manager.redis_client.xgroup_create(
            "mystream", "mygroup", id="0", mkstream=True
        )

        call_count = [0]

        def mock_xreadgroup(group, consumer, streams, count, block):
            call_count[0] += 1
            if call_count[0] >= 2:
                stream_manager.running = False
            raise RuntimeError("Unexpected error")

        original_xreadgroup = stream_manager.redis_client.xreadgroup
        stream_manager.redis_client.xreadgroup = mock_xreadgroup

        stream_manager._start_listener("mystream")
        time.sleep(0.5)

        stream_manager.redis_client.xreadgroup = original_xreadgroup
        assert call_count[0] >= 2


class TestStartListenerRuntimeError:
    """Target lines 176-177: RuntimeError on thread.start()."""

    def test_start_listener_raises_stream_error_on_runtime_error(self, stream_manager):
        """Test _start_listener raises StreamError when thread.start() fails."""
        stream_manager.consumers["mystream"] = {
            "group_name": "mygroup",
            "consumer_name": "consumer1",
            "callback": lambda x: None,
        }

        with patch("threading.Thread") as mock_thread_cls:
            mock_thread = MagicMock()
            mock_thread.start.side_effect = RuntimeError("Cannot start thread")
            mock_thread_cls.return_value = mock_thread

            with pytest.raises(StreamError, match="Failed to start listener"):
                stream_manager._start_listener("mystream")


class TestReadFromStreamDecodedMessages:
    """Target lines 198-216: decoded_messages list comprehension and return."""

    def test_read_from_stream_returns_decoded_messages(self, stream_manager):
        """Test read_from_stream returns properly decoded messages."""
        mock_result = [
            (
                b"mystream",
                [(b"1-0", {b"field1": b"value1", b"field2": b"value2"})],
            )
        ]
        with patch.object(
            stream_manager.redis_client, "xread", return_value=mock_result
        ):
            messages = stream_manager.read_from_stream("mystream", count=1, block=0)

        assert len(messages) == 1
        assert messages[0]["stream"] == "mystream"
        assert len(messages[0]["entries"]) == 1
        assert messages[0]["entries"][0]["id"] == "1-0"
        assert messages[0]["entries"][0]["data"] == {
            "field1": "value1",
            "field2": "value2",
        }

    def test_read_from_stream_returns_empty_list_no_messages(self, stream_manager):
        """Test read_from_stream returns empty list when no new messages."""
        messages = stream_manager.read_from_stream("nonexistent", count=1, block=1)

        assert messages == []

    def test_read_from_stream_multiple_entries(self, stream_manager):
        """Test read_from_stream handles multiple entries."""
        mock_result = [
            (
                b"mystream",
                [
                    (b"1-0", {b"msg": b"1"}),
                    (b"2-0", {b"msg": b"2"}),
                ],
            )
        ]
        with patch.object(
            stream_manager.redis_client, "xread", return_value=mock_result
        ):
            messages = stream_manager.read_from_stream("mystream", count=2, block=0)

        assert len(messages) == 1
        assert len(messages[0]["entries"]) == 2

    def test_read_from_stream_decodes_stream_name(self, stream_manager):
        """Test read_from_stream properly decodes stream name."""
        mock_result = [(b"myteststream", [(b"1-0", {b"key": b"val"})])]
        with patch.object(
            stream_manager.redis_client, "xread", return_value=mock_result
        ):
            messages = stream_manager.read_from_stream("myteststream", count=1, block=0)

        assert messages[0]["stream"] == "myteststream"

    def test_read_from_stream_decodes_entry_id(self, stream_manager):
        """Test read_from_stream properly decodes entry IDs."""
        mock_result = [(b"mystream", [(b"1234567890-0", {b"k": b"v"})])]
        with patch.object(
            stream_manager.redis_client, "xread", return_value=mock_result
        ):
            messages = stream_manager.read_from_stream("mystream", count=1, block=0)

        entry_id = messages[0]["entries"][0]["id"]
        assert entry_id == "1234567890-0"
        assert isinstance(entry_id, str)

    def test_read_from_stream_decodes_message_data(self, stream_manager):
        """Test read_from_stream properly decodes message data."""
        mock_result = [(b"mystream", [(b"1-0", {b"name": b"test", b"count": b"42"})])]
        with patch.object(
            stream_manager.redis_client, "xread", return_value=mock_result
        ):
            messages = stream_manager.read_from_stream("mystream", count=1, block=0)

        data = messages[0]["entries"][0]["data"]
        assert data == {"name": "test", "count": "42"}


class TestReadFromStreamValidationError:
    """Target line 218: re-raise ValidationError/StreamError in read_from_stream."""

    def test_read_from_stream_re_raises_validation_error_empty_key(
        self, stream_manager
    ):
        """Test read_from_stream re-raises ValidationError for empty key."""
        with pytest.raises(ValidationError, match="Redis key cannot be empty"):
            stream_manager.read_from_stream("", count=1)

    def test_read_from_stream_re_raises_validation_error_long_key(self, stream_manager):
        """Test read_from_stream re-raises ValidationError for too-long key."""
        long_key = "k" * 600
        with pytest.raises(ValidationError, match="Redis key too long"):
            stream_manager.read_from_stream(long_key, count=1)


class TestWait:
    """Target lines 231-236: wait() method with signal handler."""

    @patch("signal.signal")
    @patch("signal.pause")
    def test_wait_registers_sigint_handler(
        self, mock_pause, mock_signal, stream_manager
    ):
        """Test wait() registers a SIGINT handler and calls signal.pause()."""
        stream_manager.wait()

        mock_signal.assert_called_once()
        call_args = mock_signal.call_args
        assert call_args[0][0] == signal.SIGINT
        mock_pause.assert_called_once()

    @patch("signal.signal")
    @patch("signal.pause")
    def test_wait_signal_handler_calls_stop_consumers(
        self, mock_pause, mock_signal, stream_manager
    ):
        """Test the SIGINT handler inside wait() calls stop_consumers()."""

        def capture_handler(sig, handler_func):
            handler_func(sig, None)

        mock_signal.side_effect = capture_handler

        with patch.object(
            stream_manager, "stop_consumers", wraps=stream_manager.stop_consumers
        ) as mock_stop:
            stream_manager.wait()
            mock_stop.assert_called_once()

    @patch("signal.signal")
    @patch("signal.pause")
    def test_wait_signal_handler_logs_stopping(
        self, mock_pause, mock_signal, stream_manager
    ):
        """Test the SIGINT handler logs 'Stopping stream consumers'."""
        stream_manager.wait()

        mock_signal.assert_called_once()
        handler_func = mock_signal.call_args[0][1]

        with (
            patch.object(stream_manager, "log") as mock_log,
            patch.object(stream_manager, "stop_consumers"),
        ):
            handler_func(signal.SIGINT, None)
            mock_log.assert_called_with("Stopping stream consumers")
