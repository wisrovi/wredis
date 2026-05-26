"""Exhaustive tests for RedisSortedSetManager."""

from unittest.mock import patch

import pytest

from wredis.sortedset import RedisSortedSetManager


class TestRedisSortedSetManager:
    """All methods of RedisSortedSetManager."""

    def test_add_to_sorted_set(self, redis_client):
        """Test adding to sorted set."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        m.add_to_sorted_set("my_zset", 1.0, "member1")
        assert redis_client.zscore("my_zset", "member1") == 1.0

    def test_add_to_sorted_set_multiple(self, redis_client):
        """Test adding multiple members."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        m.add_to_sorted_set("my_zset", 1.0, "a")
        m.add_to_sorted_set("my_zset", 2.0, "b")
        m.add_to_sorted_set("my_zset", 3.0, "c")

        assert redis_client.zcard("my_zset") == 3

    def test_add_to_sorted_set_ttl(self, redis_client):
        """Test adding with TTL."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        m.add_to_sorted_set("my_zset", 1.0, "member1", ttl=60)
        assert redis_client.ttl("my_zset") > 0

    def test_add_to_sorted_set_error(self, redis_client):
        """Test add_to_sorted_set with error handling."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "zadd", side_effect=Exception("Redis error")):
            m.add_to_sorted_set("my_zset", 1.0, "member1")

    def test_get_sorted_set(self, redis_client):
        """Test getting sorted set."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1, "b": 2, "c": 3})
        result = m.get_sorted_set("my_zset")
        assert len(result) == 3

    def test_get_sorted_set_with_scores(self, redis_client):
        """Test getting with scores."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1.0, "b": 2.0})
        result = m.get_sorted_set("my_zset", with_scores=True)
        assert len(result) == 2

    def test_get_sorted_set_range(self, redis_client):
        """Test getting range."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1, "b": 2, "c": 3, "d": 4})
        result = m.get_sorted_set("my_zset", start=0, stop=2)
        assert len(result) == 3

    def test_get_sorted_set_error(self, redis_client):
        """Test get_sorted_set with error handling."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "zrange", side_effect=Exception("Redis error")):
            result = m.get_sorted_set("my_zset")
            assert result == []

    def test_get_sorted_set_reverse(self, redis_client):
        """Test getting in reverse."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1, "b": 2, "c": 3})
        result = m.get_sorted_set_reverse("my_zset")
        assert result[0] == "c"

    def test_get_sorted_set_reverse_with_scores(self, redis_client):
        """Test reverse with scores."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1.0, "b": 2.0})
        result = m.get_sorted_set_reverse("my_zset", with_scores=True)
        assert len(result) == 2

    def test_get_sorted_set_reverse_error(self, redis_client):
        """Test get_sorted_set_reverse with error."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(
            redis_client, "zrevrange", side_effect=Exception("Redis error")
        ):
            result = m.get_sorted_set_reverse("my_zset")
            assert result == []

    def test_get_rank(self, redis_client):
        """Test getting rank."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1, "b": 2, "c": 3})
        rank = m.get_rank("my_zset", "b")
        assert rank == 1

    def test_get_rank_not_exists(self, redis_client):
        """Test rank for non-existent."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1})
        rank = m.get_rank("my_zset", "nonexistent")
        assert rank is None

    def test_get_rank_error(self, redis_client):
        """Test get_rank with error."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "zrank", side_effect=Exception("Redis error")):
            result = m.get_rank("my_zset", "a")
            assert result is None

    def test_get_score(self, redis_client):
        """Test getting score."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1.5, "b": 2.5})
        score = m.get_score("my_zset", "b")
        assert score == 2.5

    def test_get_score_not_exists(self, redis_client):
        """Test score for non-existent."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1})
        score = m.get_score("my_zset", "nonexistent")
        assert score is None

    def test_get_score_error(self, redis_client):
        """Test get_score with error."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "zscore", side_effect=Exception("Redis error")):
            result = m.get_score("my_zset", "a")
            assert result is None

    def test_remove_from_sorted_set(self, redis_client):
        """Test removing member."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1, "b": 2})
        m.remove_from_sorted_set("my_zset", "a")
        assert redis_client.zscore("my_zset", "a") is None

    def test_remove_from_sorted_set_error(self, redis_client):
        """Test remove_from_sorted_set with error."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "zrem", side_effect=Exception("Redis error")):
            m.remove_from_sorted_set("my_zset", "a")

    def test_delete_sorted_set(self, redis_client):
        """Test deleting sorted set."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1})
        m.delete_sorted_set("my_zset")
        assert redis_client.exists("my_zset") == 0

    def test_delete_sorted_set_error(self, redis_client):
        """Test delete_sorted_set with error."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "delete", side_effect=Exception("Redis error")):
            m.delete_sorted_set("my_zset")

    def test_get_ttl_exists(self, redis_client):
        """Test getting TTL."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1})
        redis_client.expire("my_zset", 100)
        ttl = m.get_ttl("my_zset")
        assert ttl == 100

    def test_get_ttl_no_ttl(self, redis_client):
        """Test getting TTL when no TTL set."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1})
        ttl = m.get_ttl("my_zset")
        assert ttl == -1

    def test_get_ttl_not_exists(self, redis_client):
        """Test getting TTL for non-existent."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        ttl = m.get_ttl("nonexistent")
        assert ttl == -2

    def test_get_ttl_error(self, redis_client):
        """Test get_ttl with error."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "ttl", side_effect=Exception("Redis error")):
            result = m.get_ttl("my_zset")
            assert result is None

    def test_set_ttl(self, redis_client):
        """Test setting TTL on existing sorted set."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1})
        m.set_ttl("my_zset", 200)
        assert redis_client.ttl("my_zset") == 200

    def test_set_ttl_not_exists(self, redis_client):
        """Test setting TTL on non-existent sorted set."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        m.set_ttl("nonexistent", 100)

    def test_set_ttl_error(self, redis_client):
        """Test set_ttl with error."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(redis_client, "exists", side_effect=Exception("Redis error")):
            m.set_ttl("my_zset", 100)

    def test_increment_score(self, redis_client):
        """Test incrementing score."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 5})
        m.increment_score("my_zset", 3, "a")
        assert redis_client.zscore("my_zset", "a") == 8.0

    def test_increment_score_error(self, redis_client):
        """Test increment_score with error."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(
            redis_client, "zincrby", side_effect=Exception("Redis error")
        ):
            m.increment_score("my_zset", 1, "a")

    def test_get_sorted_set_by_score(self, redis_client):
        """Test getting by score range."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1, "b": 5, "c": 10})
        result = m.get_sorted_set_by_score("my_zset", 2, 8)
        assert len(result) == 1
        assert result[0] == "b"

    def test_get_sorted_set_by_score_with_scores(self, redis_client):
        """Test getting by score range with scores."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        redis_client.zadd("my_zset", {"a": 1.0, "b": 5.0})
        result = m.get_sorted_set_by_score("my_zset", 1, 5, with_scores=True)
        assert len(result) == 2

    def test_get_sorted_set_by_score_error(self, redis_client):
        """Test get_sorted_set_by_score with error."""
        m = RedisSortedSetManager(host="localhost", verbose=False)
        m.redis_client = redis_client

        with patch.object(
            redis_client, "zrangebyscore", side_effect=Exception("Redis error")
        ):
            result = m.get_sorted_set_by_score("my_zset", 1, 5)
            assert result == []
