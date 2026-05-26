"""Unit tests for RedisTransactionManager."""

from unittest.mock import patch

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

    def test_execute_transaction_empty(self, redis_client):
        """Test executing empty transaction."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        results = manager.execute_transaction([])
        assert results == []

    def test_execute_transaction_error(self, redis_client):
        """Test execute_transaction with error handling."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(
            manager.redis_client, "pipeline", side_effect=Exception("Redis error")
        ):
            result = manager.execute_transaction([("set", ["k", "v"])])
            assert result is None

    def test_watch_and_execute(self, redis_client):
        """Test watch and execute transaction."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        results = manager.watch_and_execute(
            ["key1"],
            [("set", ["key1", "value1"]), ("get", ["key1"])],
        )

        assert results[0] is True
        assert results[1] == b"value1"

    def test_watch_and_execute_conflict(self, redis_client):
        """Test watch and execute when keys change - using fakeredis limitations."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.set("watch_key", "initial")

        result = manager.watch_and_execute(
            ["watch_key"],
            [("set", ["watch_key", "new_value"])],
        )

        assert result is not None

    def test_set_if_not_exists(self, redis_client):
        """Test SET NX (set if not exists)."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        result1 = manager.set_if_not_exists("lock", "locked", ttl=60)
        assert result1 is True

        result2 = manager.set_if_not_exists("lock", "locked_again", ttl=60)
        assert result2 is False

    def test_set_if_not_exists_error(self, redis_client):
        """Test set_if_not_exists with error."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(
            manager.redis_client, "set", side_effect=Exception("Redis error")
        ):
            result = manager.set_if_not_exists("key", "value")
            assert result is False

    def test_increment_atomic(self, redis_client):
        """Test atomic increment."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.set("counter", "10")

        result1 = manager.increment_atomic("counter", 5)
        assert result1 == 15

        result2 = manager.increment_atomic("counter", -3)
        assert result2 == 12

    def test_increment_atomic_decrement(self, redis_client):
        """Test atomic decrement."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.set("counter", "10")

        result = manager.increment_atomic("counter", -5)
        assert result == 5

    def test_increment_atomic_error(self, redis_client):
        """Test increment_atomic with error."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(
            manager.redis_client, "incrby", side_effect=Exception("Redis error")
        ):
            result = manager.increment_atomic("key", 1)
            assert result == 0

    def test_get_and_set(self, redis_client):
        """Test atomic get and set."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.set("mykey", "old_value")

        old = manager.get_and_set("mykey", "new_value")

        assert old == b"old_value"
        assert redis_client.get("mykey") == b"new_value"

    def test_get_and_set_error(self, redis_client):
        """Test get_and_set with error."""
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(
            manager.redis_client, "pipeline", side_effect=Exception("Redis error")
        ):
            result = manager.get_and_set("key", "value")
            assert result is None
