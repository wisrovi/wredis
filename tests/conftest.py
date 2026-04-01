"""Tests conftest - fakeredis fixtures."""

import fakeredis
import fakeredis.aioredis
import pytest


@pytest.fixture
def redis_client():
    """Provide a fake Redis client matching production config."""
    client = fakeredis.FakeRedis()
    yield client
    client.flushall()


@pytest.fixture
def redis_client_binary():
    """Provide a fake Redis client (binary values)."""
    client = fakeredis.FakeRedis(decode_responses=False)
    yield client
    client.flushall()


@pytest.fixture
def async_redis_client():
    """Provide a fake async Redis client."""
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    return client


@pytest.fixture
def async_redis_client_binary():
    """Provide a fake async Redis client (binary values)."""
    client = fakeredis.aioredis.FakeRedis(decode_responses=False)
    return client
