"""Unit tests for RedisSetManager - full coverage."""

import pytest

from wredis.sets import RedisSetManager


class TestRedisSetManager:
    """Tests for RedisSetManager - all methods."""

    def test_add_to_set(self, redis_client):
        """Test adding elements to a set."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_to_set("my_set", "value1", "value2", "value3")
        members = redis_client.smembers("my_set")
        assert len(members) == 3

    def test_add_to_set_with_ttl(self, redis_client):
        """Test adding elements with TTL."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_to_set("my_set", "value1", ttl=60)
        ttl = redis_client.ttl("my_set")
        assert ttl > 0

    def test_get_set_members(self, redis_client):
        """Test getting all set members."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.sadd("my_set", "a", "b", "c")
        members = manager.get_set_members("my_set")
        assert len(members) == 3
        assert "a" in members

    def test_get_set_members_empty(self, redis_client):
        """Test getting members of empty set."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        members = manager.get_set_members("empty_set")
        assert len(members) == 0

    def test_is_member(self, redis_client):
        """Test checking membership."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.sadd("my_set", "value1", "value2")
        assert manager.is_member("my_set", "value1") == 1
        assert manager.is_member("my_set", "value3") == 0

    def test_is_member_nonexistent_set(self, redis_client):
        """Test membership check on nonexistent set."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        assert manager.is_member("nonexistent", "value") == 0

    def test_remove_from_set(self, redis_client):
        """Test removing elements from set."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.sadd("my_set", "value1", "value2", "value3")
        manager.remove_from_set("my_set", "value2")
        members = redis_client.smembers("my_set")
        assert len(members) == 2

    def test_remove_from_set_multiple(self, redis_client):
        """Test removing multiple elements."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.sadd("my_set", "a", "b", "c")
        manager.remove_from_set("my_set", "a", "b")
        members = redis_client.smembers("my_set")
        assert len(members) == 1

    def test_get_ttl_exists(self, redis_client):
        """Test getting TTL."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.sadd("my_set", "value1")
        redis_client.expire("my_set", 100)

        ttl = manager.get_ttl("my_set")
        assert ttl == 100

    def test_get_ttl_no_ttl(self, redis_client):
        """Test getting TTL when no TTL set."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.sadd("my_set", "value1")

        ttl = manager.get_ttl("my_set")
        assert ttl == -1

    def test_get_ttl_nonexistent(self, redis_client):
        """Test getting TTL for nonexistent key."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        ttl = manager.get_ttl("nonexistent")
        assert ttl == -2

    def test_extend_ttl(self, redis_client):
        """Test extending TTL."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.sadd("my_set", "value1")
        redis_client.expire("my_set", 10)

        manager.extend_ttl("my_set", 200)

        ttl = redis_client.ttl("my_set")
        assert ttl == 200

    def test_extend_ttl_nonexistent(self, redis_client):
        """Test extending TTL for nonexistent key."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.extend_ttl("nonexistent", 100)
