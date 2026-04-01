"""Unit tests for RedisSortedSetManager."""

import pytest

from wredis.sortedset import RedisSortedSetManager


class TestRedisSortedSetManager:
    """Tests for RedisSortedSetManager."""

    def test_add_to_sorted_set(self, redis_client):
        """Test adding to sorted set."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_to_sorted_set("my_zset", 1.0, "member1")

        assert redis_client.zscore("my_zset", "member1") == 1.0

    def test_add_to_sorted_set_with_ttl(self, redis_client):
        """Test adding with TTL."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_to_sorted_set("my_zset", 1.0, "member1", ttl=60)

        ttl = redis_client.ttl("my_zset")
        assert ttl > 0

    def test_get_sorted_set(self, redis_client):
        """Test getting sorted set members."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1, "b": 2, "c": 3})

        members = manager.get_sorted_set("my_zset")
        assert len(members) == 3

    def test_get_sorted_set_with_scores(self, redis_client):
        """Test getting sorted set with scores."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1.0, "b": 2.0})

        result = manager.get_sorted_set("my_zset", with_scores=True)
        assert len(result) == 2

    def test_get_sorted_set_reverse(self, redis_client):
        """Test getting sorted set in reverse."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1, "b": 2, "c": 3})

        members = manager.get_sorted_set_reverse("my_zset")
        assert members[0] == "c"

    def test_get_rank(self, redis_client):
        """Test getting rank of member."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1, "b": 2, "c": 3})

        rank = manager.get_rank("my_zset", "b")
        assert rank == 1

    def test_get_score(self, redis_client):
        """Test getting score of member."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1.5, "b": 2.5})

        score = manager.get_score("my_zset", "b")
        assert score == 2.5

    def test_remove_from_sorted_set(self, redis_client):
        """Test removing member from sorted set."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1, "b": 2})
        manager.remove_from_sorted_set("my_zset", "a")

        assert redis_client.zscore("my_zset", "a") is None

    def test_get_ttl_exists(self, redis_client):
        """Test getting TTL."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1})
        redis_client.expire("my_zset", 100)

        ttl = manager.get_ttl("my_zset")
        assert ttl == 100
