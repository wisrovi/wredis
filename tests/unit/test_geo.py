"""Unit tests for RedisGeoManager."""

from unittest.mock import patch

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

    def test_add_location_multiple(self, redis_client):
        """Test adding multiple locations."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_location("cities", "paris", 2.3522, 48.8566)
        manager.add_location("cities", "london", -0.1276, 51.5074)

        positions = redis_client.geopos("cities", "paris", "london")
        assert len([p for p in positions if p]) == 2

    def test_add_location_error(self, redis_client):
        """Test add_location with error."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "geoadd", side_effect=Exception("Redis error")):
            manager.add_location("cities", "test", 0, 0)

    def test_get_distance(self, redis_client):
        """Test getting distance between two locations."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_location("cities", "new_york", -74.006, 40.7128)
        manager.add_location("cities", "los_angeles", -118.2437, 34.0522)

        distance = manager.get_distance("cities", "new_york", "los_angeles", unit="km")
        assert distance is not None
        assert distance > 0

    def test_get_distance_different_units(self, redis_client):
        """Test distance with different units."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_location("cities", "a", 0, 0)
        manager.add_location("cities", "b", 1, 0)

        dist_km = manager.get_distance("cities", "a", "b", unit="km")
        dist_mi = manager.get_distance("cities", "a", "b", unit="mi")
        assert dist_km is not None
        assert dist_mi is not None

    def test_get_distance_error(self, redis_client):
        """Test get_distance with error."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "geodist", side_effect=Exception("Redis error")):
            result = manager.get_distance("cities", "a", "b")
            assert result is None

    def test_get_positions(self, redis_client):
        """Test getting positions of locations."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_location("cities", "new_york", -74.006, 40.7128)
        manager.add_location("cities", "chicago", -87.6298, 41.8781)

        positions = manager.get_positions("cities", "new_york", "chicago")
        assert len(positions) == 2

    def test_get_positions_empty(self, redis_client):
        """Test getting positions for non-existent locations."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        positions = manager.get_positions("cities", "nonexistent")
        assert len(positions) == 1
        assert positions[0] is None

    def test_get_positions_error(self, redis_client):
        """Test get_positions with error."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "geopos", side_effect=Exception("Redis error")):
            result = manager.get_positions("cities", "a")
            assert result == []

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

    def test_search_nearby_empty(self, redis_client):
        """Test searching nearby with no results."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        manager.add_location("places", "store_a", 0, 0)
        nearby = manager.search_nearby("places", 100, 100, 1, unit="km")
        assert len(nearby) == 0

    def test_search_nearby_error(self, redis_client):
        """Test search_nearby with error."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "georadius", side_effect=Exception("Redis error")):
            result = manager.search_nearby("places", 0, 0, 1)
            assert result == []

    def test_search_nearby_with_distance_error(self, redis_client):
        """Test search_nearby_with_distance with error."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "georadius", side_effect=Exception("Redis error")):
            result = manager.search_nearby_with_distance("places", 0, 0, 1)
            assert result == []
