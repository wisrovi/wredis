"""Unit tests for RedisTransactionManager."""

import pytest

from wredis.transaction import RedisTransactionManager


class TestRedisTransactionManager:
    """Tests for RedisTransactionManager."""

    def test_execute_transaction(self, redis_client):
        """Test executing multiple commands in transaction."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        results = manager.execute_transaction(
            [
                ("set", ["balance:alice", "100"]),
                ("set", ["balance:bob", "50"]),
                ("incrby", ["balance:alice", 50]),
                ("get", ["balance:alice"]),
            ]
        )

        assert results[0] is True
        assert results[1] is True
        assert results[2] == 150
        assert results[3] == b"150"

    def test_set_if_not_exists(self, redis_client):
        """Test SET NX (set if not exists)."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        result1 = manager.set_if_not_exists("lock", "locked", ttl=60)
        assert result1 is True

        result2 = manager.set_if_not_exists("lock", "locked_again", ttl=60)
        assert result2 is False

    def test_increment_atomic(self, redis_client):
        """Test atomic increment."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.set("counter", "10")

        result1 = manager.increment_atomic("counter", 5)
        assert result1 == 15

        result2 = manager.increment_atomic("counter", -3)
        assert result2 == 12

    def test_get_and_set(self, redis_client):
        """Test atomic get and set."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.set("mykey", "old_value")

        old = manager.get_and_set("mykey", "new_value")

        assert old == b"old_value"
        assert redis_client.get("mykey") == b"new_value"
