"""Tests for AsyncRedisGeoManager."""

from unittest.mock import AsyncMock

import fakeredis.aioredis
import pytest

from wredis.async_api.geo import AsyncRedisGeoManager


@pytest.fixture
async def async_client():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield fake
    await fake.aclose()


@pytest.fixture
def manager():
    return AsyncRedisGeoManager(verbose=False)


class TestAsyncRedisGeoManagerInit:
    """Tests for initialization."""

    def test_init_defaults(self):
        m = AsyncRedisGeoManager()
        assert m.verbose is True

    def test_init_custom(self):
        m = AsyncRedisGeoManager(host="myhost", port=1234, db=2, verbose=False)
        assert m.verbose is False


class TestAsyncRedisGeoManagerAddLocation:
    """Tests for add_location method."""

    @pytest.mark.asyncio
    async def test_add_single_location(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        pos = await async_client.geopos("cities", "Paris")
        assert pos is not None
        assert len(pos) == 1

    @pytest.mark.asyncio
    async def test_add_multiple_locations(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        await manager.add_location("cities", "London", -0.1276, 51.5074)
        members = await async_client.zrange("cities", 0, -1)
        assert len(members) == 2

    @pytest.mark.asyncio
    async def test_add_location_negative_coords(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "NYC", -74.0060, 40.7128)
        pos = await async_client.geopos("cities", "NYC")
        assert pos is not None

    @pytest.mark.asyncio
    async def test_add_location_error(self, manager):
        mock_client = AsyncMock()
        mock_client.geoadd.side_effect = Exception("error")
        manager.redis_client = mock_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        mock_client.geoadd.assert_called_once()


class TestAsyncRedisGeoManagerGetDistance:
    """Tests for get_distance method."""

    @pytest.mark.asyncio
    async def test_get_distance_km(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        await manager.add_location("cities", "London", -0.1276, 51.5074)
        distance = await manager.get_distance("cities", "Paris", "London", unit="km")
        assert distance is not None
        assert distance > 300

    @pytest.mark.asyncio
    async def test_get_distance_miles(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        await manager.add_location("cities", "London", -0.1276, 51.5074)
        distance = await manager.get_distance("cities", "Paris", "London", unit="mi")
        assert distance is not None
        assert distance > 200

    @pytest.mark.asyncio
    async def test_get_distance_same_location(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        distance = await manager.get_distance("cities", "Paris", "Paris", unit="km")
        assert distance == 0.0

    @pytest.mark.asyncio
    async def test_get_distance_nonexistent_location(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        distance = await manager.get_distance("cities", "Paris", "Tokyo", unit="km")
        assert distance is None

    @pytest.mark.asyncio
    async def test_get_distance_nonexistent_key(self, async_client, manager):
        manager.redis_client = async_client
        distance = await manager.get_distance("nonexistent", "Paris", "London", unit="km")
        assert distance is None

    @pytest.mark.asyncio
    async def test_get_distance_error(self, manager):
        mock_client = AsyncMock()
        mock_client.geodist.side_effect = Exception("error")
        manager.redis_client = mock_client
        distance = await manager.get_distance("cities", "Paris", "London")
        assert distance is None


class TestAsyncRedisGeoManagerGetPositions:
    """Tests for get_positions method."""

    @pytest.mark.asyncio
    async def test_get_single_position(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        positions = await manager.get_positions("cities", "Paris")
        assert len(positions) == 1
        assert positions[0][0] == "Paris"
        assert abs(positions[0][1] - 2.3522) < 0.01
        assert abs(positions[0][2] - 48.8566) < 0.01

    @pytest.mark.asyncio
    async def test_get_multiple_positions(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        await manager.add_location("cities", "London", -0.1276, 51.5074)
        positions = await manager.get_positions("cities", "Paris", "London")
        assert len(positions) == 2
        assert positions[0][0] == "Paris"
        assert positions[1][0] == "London"

    @pytest.mark.asyncio
    async def test_get_position_nonexistent_location(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        positions = await manager.get_positions("cities", "Paris", "Tokyo")
        assert len(positions) == 2
        assert positions[0] is not None
        assert positions[1] is None

    @pytest.mark.asyncio
    async def test_get_positions_empty_key(self, async_client, manager):
        manager.redis_client = async_client
        positions = await manager.get_positions("nonexistent", "Paris")
        assert positions == [None]

    @pytest.mark.asyncio
    async def test_get_positions_error(self, manager):
        mock_client = AsyncMock()
        mock_client.geopos.side_effect = Exception("error")
        manager.redis_client = mock_client
        positions = await manager.get_positions("cities", "Paris")
        assert positions == []


class TestAsyncRedisGeoManagerSearchNearby:
    """Tests for search_nearby method."""

    @pytest.mark.asyncio
    async def test_search_nearby(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        await manager.add_location("cities", "Lyon", 4.8357, 45.7640)
        await manager.add_location("cities", "London", -0.1276, 51.5074)
        results = await manager.search_nearby("cities", 2.3522, 48.8566, 500, unit="km")
        assert "Paris" in results
        assert "Lyon" in results

    @pytest.mark.asyncio
    async def test_search_nearby_with_count(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        await manager.add_location("cities", "Lyon", 4.8357, 45.7640)
        results = await manager.search_nearby("cities", 2.3522, 48.8566, 1000, unit="km", count=1)
        assert len(results) <= 1

    @pytest.mark.asyncio
    async def test_search_nearby_no_results(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        results = await manager.search_nearby("cities", 2.3522, 48.8566, 1, unit="km")
        assert "Paris" in results

    @pytest.mark.asyncio
    async def test_search_nearby_empty_key(self, async_client, manager):
        manager.redis_client = async_client
        results = await manager.search_nearby("nonexistent", 0, 0, 100, unit="km")
        assert results == []

    @pytest.mark.asyncio
    async def test_search_nearby_error(self, manager):
        mock_client = AsyncMock()
        mock_client.georadius.side_effect = Exception("error")
        manager.redis_client = mock_client
        results = await manager.search_nearby("cities", 0, 0, 100)
        assert results == []


class TestAsyncRedisGeoManagerSearchNearbyWithDistance:
    """Tests for search_nearby_with_distance method."""

    @pytest.mark.asyncio
    async def test_search_nearby_with_distance(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        await manager.add_location("cities", "Lyon", 4.8357, 45.7640)
        results = await manager.search_nearby_with_distance("cities", 2.3522, 48.8566, 500, unit="km")
        assert len(results) >= 1
        for item in results:
            assert len(item) == 2

    @pytest.mark.asyncio
    async def test_search_nearby_with_distance_count(self, async_client, manager):
        manager.redis_client = async_client
        await manager.add_location("cities", "Paris", 2.3522, 48.8566)
        await manager.add_location("cities", "Lyon", 4.8357, 45.7640)
        results = await manager.search_nearby_with_distance("cities", 2.3522, 48.8566, 1000, unit="km", count=1)
        assert len(results) <= 1

    @pytest.mark.asyncio
    async def test_search_nearby_with_distance_empty_key(self, async_client, manager):
        manager.redis_client = async_client
        results = await manager.search_nearby_with_distance("nonexistent", 0, 0, 100, unit="km")
        assert results == []

    @pytest.mark.asyncio
    async def test_search_nearby_with_distance_error(self, manager):
        mock_client = AsyncMock()
        mock_client.georadius.side_effect = Exception("error")
        manager.redis_client = mock_client
        results = await manager.search_nearby_with_distance("cities", 0, 0, 100)
        assert results == []
