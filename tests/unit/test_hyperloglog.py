"""Unit tests for RedisHyperLogLogManager."""

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

    def test_count(self, redis_client):
        """Test counting unique elements."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add("visitors", "user1", "user2", "user3")
        manager.add("visitors", "user4", "user5")

        count = manager.count("visitors")
        assert count == 5

    def test_count_multiple_keys(self, redis_client):
        """Test counting multiple keys."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.pfadd("day1", "user1", "user2", "user3")
        redis_client.pfadd("day2", "user3", "user4", "user5")

        count = manager.count("day1", "day2")
        assert count == 5

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
