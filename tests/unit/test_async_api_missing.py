"""Tests for remaining uncovered lines in async_api modules."""

from unittest.mock import AsyncMock, patch

import fakeredis.aioredis
import pytest

from wredis.async_api.hash import AsyncRedisHashManager
from wredis.async_api.hyperloglog import AsyncRedisHyperLogLogManager


class TestAsyncRedisHashManagerMissing:
    """Tests for uncovered lines in AsyncRedisHashManager."""

    @pytest.mark.asyncio
    async def test_update_hash_error(self):
        """Test update_hash with error (line 127)."""
        mgr = AsyncRedisHashManager(verbose=False)
        mock = AsyncMock()
        mock.hget.side_effect = Exception("error")
        mgr.redis_client = mock
        await mgr.update_hash("h", "f", {"data": "val"})

    @pytest.mark.asyncio
    async def test_exist_success(self):
        """Test exist method success path."""
        mgr = AsyncRedisHashManager(verbose=False)
        client = fakeredis.aioredis.FakeRedis(decode_responses=True)
        mgr.redis_client = client
        await client.hset("h", "f", "v")
        assert await mgr.exist("h") is True


class TestAsyncRedisHyperLogLogManagerMissing:
    """Tests for uncovered lines in AsyncRedisHyperLogLogManager."""

    @pytest.mark.asyncio
    async def test_exist_success(self):
        """Test exist method (lines 52-54)."""
        mgr = AsyncRedisHyperLogLogManager(verbose=False)
        client = fakeredis.aioredis.FakeRedis(decode_responses=True)
        mgr.redis_client = client
        await client.pfadd("hll", "a")
        assert await mgr.exist("hll") is True

    @pytest.mark.asyncio
    async def test_exist_nonexistent(self):
        """Test exist method returns False for missing key."""
        mgr = AsyncRedisHyperLogLogManager(verbose=False)
        client = fakeredis.aioredis.FakeRedis(decode_responses=True)
        mgr.redis_client = client
        assert await mgr.exist("nonexistent") is False

    @pytest.mark.asyncio
    async def test_exist_error(self):
        """Test exist method with error (line 55-57)."""
        mgr = AsyncRedisHyperLogLogManager(verbose=False)
        mock = AsyncMock()
        mock.exists.side_effect = Exception("error")
        mgr.redis_client = mock
        assert await mgr.exist("hll") is False
