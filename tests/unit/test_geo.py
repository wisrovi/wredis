"""Unit tests for RedisGeoManager."""

import pytest

from wredis.geo import RedisGeoManager


class TestRedisGeoManager:
    """Tests for RedisGeoManager."""

    def test_add_location(self, redis_client):
        """Test adding a location to geo key."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_location("cities", "new_york", -74.006, 40.7128)

        positions = redis_client.geopos("cities", "new_york")
        assert positions is not None

    def test_get_distance(self, redis_client):
        """Test getting distance between two locations."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_location("cities", "new_york", -74.006, 40.7128)
        manager.add_location("cities", "los_angeles", -118.2437, 34.0522)

        distance = manager.get_distance("cities", "new_york", "los_angeles", unit="km")
        assert distance is not None
        assert distance > 0

    def test_get_positions(self, redis_client):
        """Test getting positions of locations."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_location("cities", "new_york", -74.006, 40.7128)
        manager.add_location("cities", "chicago", -87.6298, 41.8781)

        positions = manager.get_positions("cities", "new_york", "chicago")
        assert len(positions) == 2

    def test_search_nearby(self, redis_client):
        """Test searching for nearby locations."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_location("places", "store_a", -122.4194, 37.7749)
        manager.add_location("places", "store_b", -122.4084, 37.7849)

        nearby = manager.search_nearby("places", -122.4194, 37.7749, 2, unit="km")
        assert len(nearby) > 0

    def test_search_nearby_with_distance(self, redis_client):
        """Test searching nearby with distances."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_location("places", "store_a", -122.4194, 37.7749)
        manager.add_location("places", "store_b", -122.4084, 37.7849)

        nearby = manager.search_nearby_with_distance("places", -122.4194, 37.7749, 5, unit="km")
        assert len(nearby) > 0
