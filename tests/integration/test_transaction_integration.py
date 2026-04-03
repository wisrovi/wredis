"""Integration tests for RedisTransactionManager con Redis real."""

import threading
import time

from wredis.transaction import RedisTransactionManager


class TestTransactionIntegration:
    """Integration tests con Redis real."""

    def test_execute_transaction(self, real_redis):
        """Test transaction con Redis real."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        results = manager.execute_transaction(
            [
                ("set", ["tx_key1", "value1"]),
                ("set", ["tx_key2", "value2"]),
                ("get", ["tx_key1"]),
            ]
        )

        assert results[0] is True
        assert results[1] is True
        assert results[2] == b"value1"

    def test_watch_and_execute_success(self, real_redis):
        """Test WATCH sin conflicto."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        real_redis.set("safe_key", "initial")

        result = manager.watch_and_execute(
            ["safe_key"],
            [("set", ["safe_key", "new_value"])],
        )

        assert result is not None
        assert result[0] is True

    def test_set_if_not_exists(self, real_redis):
        """Test SET NX con Redis real."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        result1 = manager.set_if_not_exists("nx_key", "first")
        assert result1 is True

        result2 = manager.set_if_not_exists("nx_key", "second")
        assert result2 is False

    def test_increment_atomic(self, real_redis):
        """Test atomic increment con Redis real."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        real_redis.set("counter", "10")

        result = manager.increment_atomic("counter", 5)
        assert result == 15

        result = manager.increment_atomic("counter", -3)
        assert result == 12

    def test_get_and_set(self, real_redis):
        """Test atomic get and set con Redis real."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        real_redis.set("mykey", "old_value")

        old = manager.get_and_set("mykey", "new_value")

        assert old == b"old_value"
        assert real_redis.get("mykey") == b"new_value"
