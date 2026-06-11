"""Unit tests for RedisBitmapManager."""

from unittest.mock import patch

import pytest

from wredis.bitmap import RedisBitmapManager


class TestRedisBitmapManager:
    """Tests for RedisBitmapManager."""

    def test_set_bit(self, redis_client):
        """Test setting a bit in a bitmap."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.set_bit("my_bitmap", 5, 1)

        bit = redis_client.getbit("my_bitmap", 5)
        assert bit == 1

    def test_set_bit_with_ttl(self, redis_client):
        """Test setting a bit with TTL."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.set_bit("my_bitmap", 10, 1, ttl=60)

        ttl = redis_client.ttl("my_bitmap")
        assert ttl > 0

    def test_set_bit_error(self, redis_client):
        """Test set_bit with error handling."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(redis_client, "setbit", side_effect=Exception("Redis error")):
            manager.set_bit("my_bitmap", 0, 1)

    def test_get_bit(self, redis_client):
        """Test getting a bit from a bitmap."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.setbit("my_bitmap", 5, 1)

        bit = manager.get_bit("my_bitmap", 5)
        assert bit == 1

    def test_get_bit_default(self, redis_client):
        """Test getting a bit that doesn't exist."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        bit = manager.get_bit("nonexistent", 0)
        assert bit == 0

    def test_get_bit_error(self, redis_client):
        """Test get_bit with error handling."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(redis_client, "getbit", side_effect=Exception("Redis error")):
            result = manager.get_bit("my_bitmap", 0)
            assert result == 0

    def test_count_bits(self, redis_client):
        """Test counting bits in a bitmap."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.setbit("my_bitmap", 0, 1)
        redis_client.setbit("my_bitmap", 1, 1)
        redis_client.setbit("my_bitmap", 2, 0)

        count = manager.count_bits("my_bitmap")
        assert count == 2

    def test_count_bits_empty(self, redis_client):
        """Test counting bits in empty bitmap."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        count = manager.count_bits("empty_bitmap")
        assert count == 0

    def test_count_bits_error(self, redis_client):
        """Test count_bits with error handling."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(redis_client, "bitcount", side_effect=Exception("Redis error")):
            result = manager.count_bits("my_bitmap")
            assert result == 0

    def test_get_ttl_exists(self, redis_client):
        """Test getting TTL for existing key."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.set("my_key", "value")
        redis_client.expire("my_key", 100)

        ttl = manager.get_ttl("my_key")
        assert ttl > 0

    def test_get_ttl_no_ttl(self, redis_client):
        """Test getting TTL when no TTL set."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.set("my_key", "value")

        ttl = manager.get_ttl("my_key")
        assert ttl == -1

    def test_get_ttl_nonexistent(self, redis_client):
        """Test getting TTL for nonexistent key."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        ttl = manager.get_ttl("nonexistent_key")
        assert ttl == -2

    def test_get_ttl_error(self, redis_client):
        """Test get_ttl with error handling."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(redis_client, "ttl", side_effect=Exception("Redis error")):
            result = manager.get_ttl("my_key")
            assert result == -2

    def test_extend_ttl(self, redis_client):
        """Test extending TTL."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.set("my_key", "value")
        redis_client.expire("my_key", 10)

        manager.extend_ttl("my_key", 200)

        ttl = redis_client.ttl("my_key")
        assert ttl == 200

    def test_extend_ttl_nonexistent(self, redis_client):
        """Test extending TTL for nonexistent key."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.extend_ttl("nonexistent", 100)

    def test_extend_ttl_error(self, redis_client):
        """Test extend_ttl with error handling."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(redis_client, "exists", side_effect=Exception("Redis error")):
            manager.extend_ttl("my_key", 100)
