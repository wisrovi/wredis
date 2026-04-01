"""Pytest configuration and fixtures for examples tests."""

import os
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure pytest
pytest_plugins = ["pytest_asyncio"]


def get_redis_host() -> str:
    """Get Redis host from environment or default."""
    return os.environ.get("REDIS_HOST", "localhost")


def get_redis_port() -> int:
    """Get Redis port from environment or default."""
    return int(os.environ.get("REDIS_PORT", "6379"))


@pytest.fixture(scope="session")
def redis_host() -> str:
    """Redis host fixture."""
    return get_redis_host()


@pytest.fixture(scope="session")
def redis_port() -> int:
    """Redis port fixture."""
    return get_redis_port()


@pytest.fixture
def hash_manager(redis_host, redis_port):
    """Create a RedisHashManager for testing."""
    from wredis.hash import RedisHashManager

    return RedisHashManager(host=redis_host, port=redis_port, verbose=False)


@pytest.fixture
def bitmap_manager(redis_host, redis_port):
    """Create a RedisBitmapManager for testing."""
    from wredis.bitmap import RedisBitmapManager

    return RedisBitmapManager(host=redis_host, port=redis_port, verbose=False)


@pytest.fixture
def set_manager(redis_host, redis_port):
    """Create a RedisSetManager for testing."""
    from wredis.sets import RedisSetManager

    return RedisSetManager(host=redis_host, port=redis_port, verbose=False)


@pytest.fixture
def sorted_set_manager(redis_host, redis_port):
    """Create a RedisSortedSetManager for testing."""
    from wredis.sortedset import RedisSortedSetManager

    return RedisSortedSetManager(host=redis_host, port=redis_port, verbose=False)


@pytest.fixture
def queue_manager(redis_host, redis_port):
    """Create a RedisQueueManager for testing."""
    from wredis.queue import RedisQueueManager

    return RedisQueueManager(host=redis_host, port=redis_port, verbose=False)


@pytest.fixture
def pubsub_manager(redis_host, redis_port):
    """Create a RedisPubSubManager for testing."""
    from wredis.pubsub import RedisPubSubManager

    return RedisPubSubManager(host=redis_host, port=redis_port, verbose=False)


@pytest.fixture
def stream_manager(redis_host, redis_port):
    """Create a RedisStreamManager for testing."""
    from wredis.streams import RedisStreamManager

    return RedisStreamManager(host=redis_host, port=redis_port, verbose=False)


@pytest.fixture
def cache_decorator():
    """Import cache decorator for testing."""
    from wredis.decorators import cache

    return cache


@pytest.fixture(autouse=True)
def cleanup_redis(hash_manager, bitmap_manager, set_manager, sorted_set_manager, queue_manager):
    """Cleanup Redis after each test."""
    yield
    # Cleanup
    try:
        for key in ["test:hash", "test:bitmap", "test:set", "test:sorted", "test:queue"]:
            try:
                hash_manager.redis_client.delete(key)
            except Exception:
                pass
    except Exception:
        pass
