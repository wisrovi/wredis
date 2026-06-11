"""Exhaustive tests for RedisHashManager - 100% coverage."""

import json
from unittest.mock import patch

import pytest

from wredis.hash import RedisHashManager


class TestRedisHashManager:
    """All methods of RedisHashManager."""

    def test_create_hash_with_dict(self, redis_client):
        """Test creating hash with dict value."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        m.create_hash("my_hash", "key1", {"name": "Alice", "age": 30})
        assert redis_client.hexists("my_hash", "key1")

    def test_create_hash_with_string(self, redis_client):
        """Test creating hash with string value."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        m.create_hash("my_hash", "key1", "plain string")
        value = redis_client.hget("my_hash", "key1")
        assert value == b"plain string"

    def test_create_hash_with_ttl(self, redis_client):
        """Test creating hash with TTL."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        m.create_hash("my_hash", "key1", {"data": "value"}, ttl=60)
        ttl = redis_client.ttl("my_hash")
        assert ttl > 0

    def test_create_hash_error(self, redis_client):
        """Test create_hash with error handling."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "hset", side_effect=Exception("Redis error")):
            m.create_hash("my_hash", "key1", "value")

    def test_exist(self, redis_client):
        """Test existence check."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.hset("my_hash", "key1", b"value")
        assert m.exist("my_hash") is True
        assert m.exist("nonexistent") is False

    def test_exist_error(self, redis_client):
        """Test exist with error handling."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "exists", side_effect=Exception("Redis error")):
            assert m.exist("my_hash") is False

    def test_read_hash_exists(self, redis_client):
        """Test reading existing hash field."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.hset("my_hash", "key1", json.dumps({"name": "Alice"}).encode())
        result = m.read_hash("my_hash", "key1")
        assert result == {"name": "Alice"}

    def test_read_hash_not_exists(self, redis_client):
        """Test reading non-existent field."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        result = m.read_hash("my_hash", "nonexistent")
        assert result is None

    def test_read_hash_plain_string(self, redis_client):
        """Test reading plain string value."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.hset("my_hash", "key1", b"plain text")
        result = m.read_hash("my_hash", "key1")
        assert result == "plain text"

    def test_read_hash_invalid_json(self, redis_client):
        """Test reading invalid JSON returns as string."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.hset("my_hash", "key1", b"not json")
        result = m.read_hash("my_hash", "key1")
        assert result == "not json"

    def test_read_hash_error(self, redis_client):
        """Test read_hash with error handling."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "hget", side_effect=Exception("Redis error")):
            result = m.read_hash("my_hash", "key1")
            assert result is None

    def test_update_hash_existing(self, redis_client):
        """Test updating existing hash field."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.hset("my_hash", "key1", json.dumps({"name": "Alice"}).encode())
        m.update_hash("my_hash", "key1", {"age": 25})

        result = m.read_hash("my_hash", "key1")
        assert result.get("age") == 25

    def test_update_hash_new_field(self, redis_client):
        """Test updating with new field."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        m.update_hash("my_hash", "key1", {"new": "value"})
        result = m.read_hash("my_hash", "key1")
        assert result.get("new") == "value"

    def test_update_hash_error(self, redis_client):
        """Test update_hash with error handling."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(m, "read_hash", side_effect=Exception("Redis error")):
            m.update_hash("my_hash", "key1", {"new": "value"})

    def test_delete_hash_field_exists(self, redis_client):
        """Test deleting existing field."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.hset("my_hash", "key1", b"value")
        m.delete_hash_field("my_hash", "key1")
        assert not redis_client.hexists("my_hash", "key1")

    def test_delete_hash_field_not_exists(self, redis_client):
        """Test deleting non-existent field."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        m.delete_hash_field("my_hash", "nonexistent")

    def test_delete_hash_field_error(self, redis_client):
        """Test delete_hash_field with error."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "hdel", side_effect=Exception("Redis error")):
            m.delete_hash_field("my_hash", "key1")

    def test_read_all_hash_exists(self, redis_client):
        """Test reading all hash fields."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.hset("my_hash", "k1", json.dumps({"a": 1}).encode())
        redis_client.hset("my_hash", "k2", json.dumps({"b": 2}).encode())

        result = m.read_all_hash("my_hash")
        assert len(result) == 2

    def test_read_all_hash_empty(self, redis_client):
        """Test reading empty hash."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        result = m.read_all_hash("empty_hash")
        assert result is None

    def test_read_all_hash_error(self, redis_client):
        """Test read_all_hash with error."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "hgetall", side_effect=Exception("Redis error")):
            result = m.read_all_hash("my_hash")
            assert result is None

    def test_get_ttl_exists_with_ttl(self, redis_client):
        """Test TTL when TTL is set."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.hset("my_hash", "key1", b"value")
        redis_client.expire("my_hash", 100)

        ttl = m.get_ttl("my_hash")
        assert ttl == 100

    def test_get_ttl_no_ttl(self, redis_client):
        """Test TTL when no TTL set."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.hset("my_hash", "key1", b"value")

        ttl = m.get_ttl("my_hash")
        assert ttl == -1

    def test_get_ttl_not_exists(self, redis_client):
        """Test TTL for non-existent key."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        ttl = m.get_ttl("nonexistent")
        assert ttl == -2

    def test_get_ttl_error(self, redis_client):
        """Test get_ttl with error."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "ttl", side_effect=Exception("Redis error")):
            result = m.get_ttl("my_hash")
            assert result is None

    def test_extend_ttl_exists(self, redis_client):
        """Test extending TTL for existing key."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.hset("my_hash", "key1", b"value")
        redis_client.expire("my_hash", 10)
        m.extend_ttl("my_hash", 200)

        assert redis_client.ttl("my_hash") == 200

    def test_extend_ttl_not_exists(self, redis_client):
        """Test extending TTL for non-existent key."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        m.extend_ttl("nonexistent", 100)

    def test_extend_ttl_error(self, redis_client):
        """Test extend_ttl with error."""
        m = RedisHashManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "exists", side_effect=Exception("Redis error")):
            m.extend_ttl("my_hash", 100)
