"""Unit tests for RedisPubSubManager - full coverage."""

import pytest

from wredis.pubsub import RedisPubSubManager


class TestRedisPubSubManager:
    """Tests for RedisPubSubManager - all methods."""

    def test_publish_message(self, redis_client):
        """Test publishing a message."""
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.publish_message("my_channel", "Hello World")

    def test_publish_message_dict(self, redis_client):
        """Test publishing a dict message."""
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.publish_message("my_channel", {"key": "value"})

    def test_publish_message_int(self, redis_client):
        """Test publishing an int message."""
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.publish_message("my_channel", 123)

    def test_on_message(self, redis_client):
        """Test registering a message handler."""
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        @manager.on_message("my_channel")
        def handler(msg):
            pass

        assert "my_channel" in manager.subscribers

    def test_on_message_multiple(self, redis_client):
        """Test registering multiple handlers."""
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        @manager.on_message("channel1")
        def handler1(msg):
            pass

        @manager.on_message("channel2")
        def handler2(msg):
            pass

        assert "channel1" in manager.subscribers
        assert "channel2" in manager.subscribers

    def test_stop_listeners(self, redis_client):
        """Test stopping all listeners."""
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.threads = []
        manager.stop_listeners()

    def test_log_info(self, redis_client):
        """Test logging with info level."""
        manager = RedisPubSubManager(host="localhost", verbose=True)
        manager.redis_client = redis_client

        manager.log("Test message", "info")

    def test_log_warning(self, redis_client):
        """Test logging with warning level."""
        manager = RedisPubSubManager(host="localhost", verbose=True)
        manager.redis_client = redis_client

        manager.log("Test warning", "warning")

    def test_log_error(self, redis_client):
        """Test logging with error level."""
        manager = RedisPubSubManager(host="localhost", verbose=True)
        manager.redis_client = redis_client

        manager.log("Test error", "error")
