"""Unit tests for RedisHyperLogLogManager."""

from unittest.mock import patch

import pytest

from wredis.hyperloglog import RedisHyperLogLogManager


class TestRedisHyperLogLogManager:
    """Tests for RedisHyperLogLogManager."""

    def test_add(self, redis_client):
        """Test adding elements to HyperLogLog."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add("visitors", "user1", "user2", "user3")

        count = redis_client.pfcount("visitors")
        assert count == 3

    def test_add_multiple(self, redis_client):
        """Test adding multiple times."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add("visitors", "user1", "user2")
        manager.add("visitors", "user3")

        count = redis_client.pfcount("visitors")
        assert count == 3

    def test_add_error(self, redis_client):
        """Test add with error handling."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "pfadd", side_effect=Exception("Redis error")):
            manager.add("visitors", "user1")

    def test_count(self, redis_client):
        """Test counting unique elements."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add("visitors", "user1", "user2", "user3")
        manager.add("visitors", "user4", "user5")

        count = manager.count("visitors")
        assert count == 5

    def test_count_empty(self, redis_client):
        """Test counting empty key."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        count = manager.count("nonexistent")
        assert count == 0

    def test_count_multiple_keys(self, redis_client):
        """Test counting multiple keys."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.pfadd("day1", "user1", "user2", "user3")
        redis_client.pfadd("day2", "user3", "user4", "user5")

        count = manager.count("day1", "day2")
        assert count == 5

    def test_count_error(self, redis_client):
        """Test count with error handling."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "pfcount", side_effect=Exception("Redis error")):
            result = manager.count("key")
            assert result == 0

    def test_merge(self, redis_client):
        """Test merging HyperLogLogs."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add("day1", "user1", "user2", "user3")
        manager.add("day2", "user3", "user4", "user5")
        manager.add("day3", "user1", "user5", "user6")

        manager.merge("total", "day1", "day2", "day3")

        count = redis_client.pfcount("total")
        assert count == 6

    def test_merge_error(self, redis_client):
        """Test merge with error handling."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "pfmerge", side_effect=Exception("Redis error")):
            manager.merge("dest", "src1", "src2")

    def test_get_all(self, redis_client):
        """Test getting all elements."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        result = manager.get_all("nonexistent")
        assert result == set()

    def test_get_all_existing(self, redis_client):
        """Test get_all for existing key."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.set("myhll_string", "some_value")
        result = manager.get_all("myhll_string")
        assert result == {"myhll_string"}

    def test_get_all_error(self, redis_client):
        """Test get_all with error handling."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "get", side_effect=Exception("Redis error")):
            result = manager.get_all("key")
            assert result is None
