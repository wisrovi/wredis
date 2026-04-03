"""Integration tests for RedisPubSubManager con Redis real."""

import threading
import time

from wredis.pubsub import RedisPubSubManager


class TestPubSubIntegration:
    """Integration tests con Redis real."""

    def test_publish_and_receive_message(self, real_redis):
        """Test pub/sub con Redis real."""
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        received_messages = []

        @manager.on_message("test_channel")
        def handler(msg):
            received_messages.append(msg)

        time.sleep(0.5)

        manager.publish_message("test_channel", "hello")
        time.sleep(1)

        assert len(received_messages) > 0
        assert "hello" in received_messages

    def test_publish_json_message(self, real_redis):
        """Test pub/sub con JSON."""
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        received_messages = []

        @manager.on_message("json_channel")
        def handler(msg):
            received_messages.append(msg)

        time.sleep(0.5)

        manager.publish_message("json_channel", {"action": "test", "value": 42})
        time.sleep(1)

        assert len(received_messages) > 0
        assert received_messages[0].get("action") == "test"

    def test_stop_listeners(self, real_redis):
        """Test stop listeners."""
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        @manager.on_message("stop_channel")
        def handler(msg):
            pass

        assert len(manager.subscribers) > 0
        manager.stop_listeners()
        assert len(manager.subscribers) == 0
