"""Unit tests for RedisHashManager."""

import json

import pytest

from wredis.hash import RedisHashManager


class TestRedisHashManager:
    """Tests for RedisHashManager."""

    def test_create_hash(self, redis_client):
        """Test creating a hash."""
        manager = RedisHashManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.create_hash("my_hash", "user:1", {"name": "Alice", "age": 30}, ttl=60)

        assert redis_client.hexists("my_hash", "user:1")

    def test_read_hash(self, redis_client):
        """Test reading a specific field."""
        manager = RedisHashManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.hset("my_hash", "user:1", json.dumps({"name": "Alice", "age": 30}))

        result = manager.read_hash("my_hash", "user:1")
        assert result == {"name": "Alice", "age": 30}

    def test_read_all_hash(self, redis_client):
        """Test reading all fields."""
        manager = RedisHashManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.hset("my_hash", "user:1", json.dumps({"name": "Alice"}))
        redis_client.hset("my_hash", "user:2", json.dumps({"name": "Bob"}))

        result = manager.read_all_hash("my_hash")
        assert len(result) == 2

    def test_update_hash(self, redis_client):
        """Test updating a hash field."""
        manager = RedisHashManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.hset("my_hash", "user:1", json.dumps({"name": "Alice"}))
        manager.update_hash("my_hash", "user:1", {"age": 25})

        result = redis_client.hget("my_hash", "user:1")
        assert b"age" in result

    def test_delete_hash_field(self, redis_client):
        """Test deleting a field."""
        manager = RedisHashManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.hset("my_hash", "user:1", json.dumps({"name": "Alice"}))
        manager.delete_hash_field("my_hash", "user:1")

        assert not redis_client.hexists("my_hash", "user:1")

    def test_get_ttl(self, redis_client):
        """Test getting TTL."""
        manager = RedisHashManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.create_hash("my_hash", "user:1", {"name": "Alice"}, ttl=60)

        ttl = manager.get_ttl("my_hash")
        assert ttl > 0
