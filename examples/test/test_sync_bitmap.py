"""Tests for sync/basic/bitmap examples."""

import sys
from pathlib import Path


def test_example_01_create():
    """Test bitmap creation example."""
    from wredis.bitmap import RedisBitmapManager

    m = RedisBitmapManager(host="localhost", verbose=False)
    m.set_bit("test:bitmap", 0, 1)
    result = m.get_bit("test:bitmap", 0)
    assert result == 1
    m.redis_client.delete("test:bitmap")


def test_example_02_read():
    """Test bitmap read example."""
    from wredis.bitmap import RedisBitmapManager

    m = RedisBitmapManager(host="localhost", verbose=False)
    m.set_bit("test:bitmap", 5, 1)
    result = m.get_bit("test:bitmap", 5)
    assert result == 1
    m.redis_client.delete("test:bitmap")


def test_count_bits():
    """Test count bits example."""
    from wredis.bitmap import RedisBitmapManager

    m = RedisBitmapManager(host="localhost", verbose=False)
    m.set_bit("test:bitmap", 0, 1)
    m.set_bit("test:bitmap", 2, 1)
    m.set_bit("test:bitmap", 4, 1)
    count = m.count_bits("test:bitmap")
    assert count == 3
    m.redis_client.delete("test:bitmap")


def test_bitmap_ttl():
    """Test bitmap TTL example."""
    from wredis.bitmap import RedisBitmapManager

    m = RedisBitmapManager(host="localhost", verbose=False)
    m.set_bit("test:bitmap", 0, 1, ttl=10)
    ttl = m.get_ttl("test:bitmap")
    assert ttl > 0 and ttl <= 10
    m.redis_client.delete("test:bitmap")


def test_bitmap_extend_ttl():
    """Test bitmap extend TTL example."""
    from wredis.bitmap import RedisBitmapManager

    m = RedisBitmapManager(host="localhost", verbose=False)
    m.set_bit("test:bitmap", 0, 1, ttl=5)
    m.extend_ttl("test:bitmap", 60)
    ttl = m.get_ttl("test:bitmap")
    assert ttl > 5
    m.redis_client.delete("test:bitmap")
