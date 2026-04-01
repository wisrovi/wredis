"""Unit tests for AsyncRedisGeoManager."""

import pytest

from wredis.async_api import AsyncRedisGeoManager


class TestAsyncRedisGeoManager:
    """Tests for AsyncRedisGeoManager."""

    @pytest.mark.asyncio
    async def test_add_location(self, async_redis_client):
        """Test adding a location to geo key."""
        manager = AsyncRedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        await manager.add_location("cities", "new_york", -74.006, 40.7128)

        positions = await async_redis_client.geopos("cities", "new_york")
        assert positions is not None

    @pytest.mark.asyncio
    async def test_get_distance(self, async_redis_client):
        """Test getting distance between two locations."""
        manager = AsyncRedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        await manager.add_location("cities", "new_york", -74.006, 40.7128)
        await manager.add_location("cities", "los_angeles", -118.2437, 34.0522)

        distance = await manager.get_distance("cities", "new_york", "los_angeles", unit="km")
        assert distance is not None
        assert distance > 0

    @pytest.mark.asyncio
    async def test_search_nearby(self, async_redis_client):
        """Test searching for nearby locations."""
        manager = AsyncRedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = async_redis_client

        await manager.add_location("places", "store_a", -122.4194, 37.7749)
        await manager.add_location("places", "store_b", -122.4084, 37.7849)

        nearby = await manager.search_nearby("places", -122.4194, 37.7749, 2, unit="km")
        assert len(nearby) > 0
