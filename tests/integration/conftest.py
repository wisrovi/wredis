"""Integration tests conftest - Real Redis fixtures."""

import os

import pytest
import redis


def get_redis_host():
    """Get Redis host from environment or default."""
    return os.environ.get("REDIS_HOST", "192.168.1.137")


def get_redis_port():
    """Get Redis port from environment or default."""
    return int(os.environ.get("REDIS_PORT", "6379"))


@pytest.fixture
def real_redis():
    """Provide a real Redis client for integration tests."""
    host = get_redis_host()
    port = get_redis_port()
    client = redis.Redis(host=host, port=port, db=15, socket_timeout=5)
    client.flushdb()
    yield client
    client.flushdb()
