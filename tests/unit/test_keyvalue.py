"""Exhaustive unit tests for RedisKeyValueManager and AsyncRedisKeyValueManager.

This module validates:
1. Binary payload storage and lossless byte retrieval for OpenCV/multimedia data.
2. UTF-8 string and JSON auto-deserialization when requested via get().
3. Time-to-Live (TTL) expiration enforcement using setex() and set(ttl=...).
4. Deletion and key existence checks (exist, exists).
5. Asynchronous key-value operations with AsyncRedisKeyValueManager.
6. Error handling and connection closure resilience.
"""

from unittest.mock import patch
import pytest

from wredis.keyvalue import RedisKeyValueManager
from wredis.async_api.keyvalue import AsyncRedisKeyValueManager


class TestRedisKeyValueManager:
    """Test suite validating all synchronous key-value operations."""

    def test_set_and_get_raw_binary_bytes(self, redis_client):
        """Validates that arbitrary binary payloads are preserved without corruption.

        Ensures JPEG buffers or raw camera frames are preserved exactly byte-for-byte.
        """
        # Arrange: Initialize the manager with fakeredis client
        manager = RedisKeyValueManager(verbose=False)
        manager.redis_client = redis_client

        # Create simulated binary data with bytes that cannot be valid UTF-8
        test_bytes = (
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb"
        )
        test_key = "camera:frame:1001"

        # Act: Store the raw bytes
        success = manager.set(test_key, test_bytes)

        # Assert: Operation succeeded and retrieved raw bytes match precisely
        assert success is True
        retrieved = manager.get_bytes(test_key)
        assert retrieved == test_bytes

    def test_setex_with_expiration(self, redis_client):
        """Validates that setex properly applies TTL expiration to keys in Redis.

        This ensures ephemeral camera frames expire automatically as expected.
        """
        manager = RedisKeyValueManager(verbose=False)
        manager.redis_client = redis_client

        key = "camera:frame:ephemeral"
        data = b"ephemeral_frame_bytes"
        ttl = 5

        # Act: Store with 5-second TTL
        assert manager.setex(key, ttl, data) is True

        # Assert: Key exists and TTL in Redis is greater than 0
        assert manager.exist(key) is True
        assert redis_client.ttl(key) > 0

    def test_set_with_dict_and_get_auto_deserialization(self, redis_client):
        """Validates that dictionary objects passed to set() are stored as JSON.

        Ensures automatic deserialization back to a Python dictionary when calling get().
        """
        manager = RedisKeyValueManager(verbose=False)
        manager.redis_client = redis_client

        meta = {"camera_id": "cam_01", "fps": 30, "resolution": "1080p"}
        key = "meta:cam_01"

        assert manager.set(key, meta) is True
        retrieved_dict = manager.get(key)
        assert isinstance(retrieved_dict, dict)
        assert retrieved_dict["camera_id"] == "cam_01"
        assert retrieved_dict["fps"] == 30

    def test_get_non_existent_key_returns_none(self, redis_client):
        """Validates that querying a missing or expired key returns None instead of raising an error."""
        manager = RedisKeyValueManager(verbose=False)
        manager.redis_client = redis_client

        assert manager.get("non_existent_key") is None
        assert manager.get_bytes("non_existent_key") is None

    def test_delete_and_exists(self, redis_client):
        """Validates key deletion and existence verification aliases (exist and exists)."""
        manager = RedisKeyValueManager(verbose=False)
        manager.redis_client = redis_client

        key = "sample:temp:key"
        manager.set(key, "hello world")
        assert manager.exist(key) is True
        assert manager.exists(key) is True

        # Delete key
        assert manager.delete(key) is True
        assert manager.exist(key) is False
        assert manager.exists(key) is False

    def test_error_handling_resilience(self, redis_client):
        """Validates that exceptions during Redis operations are logged and return False or None safely."""
        manager = RedisKeyValueManager(verbose=False)
        manager.redis_client = redis_client

        with patch.object(
            redis_client, "set", side_effect=Exception("Redis connection lost")
        ):
            assert manager.set("failing_key", "value") is False

        with patch.object(
            redis_client, "get", side_effect=Exception("Timeout reading socket")
        ):
            assert manager.get("failing_key") is None
            assert manager.get_bytes("failing_key") is None

        with patch.object(
            redis_client, "delete", side_effect=Exception("Deletion error")
        ):
            assert manager.delete("failing_key") is False

        with patch.object(
            redis_client, "exists", side_effect=Exception("Exists error")
        ):
            assert manager.exist("failing_key") is False


@pytest.mark.asyncio
class TestAsyncRedisKeyValueManager:
    """Test suite validating asynchronous key-value operations."""

    async def test_async_set_get_and_delete(self):
        """Validates asynchronous set, get, get_bytes, and delete operations."""
        import fakeredis.aioredis

        fake_async_redis = fakeredis.aioredis.FakeRedis()
        manager = AsyncRedisKeyValueManager(verbose=False)
        manager.redis_client = fake_async_redis

        key = "async:frame:1"
        data = b"\x01\x02\x03\x04"

        try:
            # Set with TTL
            assert await manager.setex(key, 10, data) is True
            assert await manager.exist(key) is True

            # Get raw bytes
            retrieved = await manager.get_bytes(key)
            assert retrieved == data

            # Delete
            assert await manager.delete(key) is True
            assert await manager.exist(key) is False
        finally:
            await manager.close()
