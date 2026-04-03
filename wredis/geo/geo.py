"""Redis Geo Manager - Geographic operations with Redis."""

from typing import Any

import redis
from loguru import logger


class RedisGeoManager:
    """Manages Redis geographic operations.

    Attributes:
        redis_client: Redis client instance.
        verbose: Enables detailed logging if True.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        verbose: bool = True,
    ):
        """Initialize the RedisGeoManager."""
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.verbose = verbose

    def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    def add_location(self, key: str, location: str, longitude: float, latitude: float) -> None:
        """Add a location to a geo key.

        Args:
            key: The geo key.
            location: The location name.
            longitude: Longitude coordinate.
            latitude: Latitude coordinate.
        """
        try:
            self.redis_client.geoadd(key, (longitude, latitude, location))
            self.log(f"Added location '{location}' to key '{key}'")
        except Exception as e:
            logger.error(f"Error adding location to key '{key}': {e}")

    def get_distance(self, key: str, location1: str, location2: str, unit: str = "km") -> float | None:
        """Get distance between two locations.

        Args:
            key: The geo key.
            location1: First location name.
            location2: Second location name.
            unit: Unit of measurement (km, mi, ft).

        Returns:
            Distance in the specified unit, or None on error.
        """
        try:
            distance = self.redis_client.geodist(key, location1, location2, unit=unit)
            self.log(f"Distance between {location1} and {location2}: {distance} {unit}")
            return distance
        except Exception as e:
            logger.error(f"Error getting distance: {e}")
            return None

    def get_positions(self, key: str, *locations: str) -> list[tuple[str, float, float] | None]:
        """Get positions of locations.

        Args:
            key: The geo key.
            locations: Location names.

        Returns:
            List of (name, lon, lat) tuples.
        """
        try:
            results = self.redis_client.geopos(key, *locations)
            positions = []
            for i, pos in enumerate(results):
                if pos:
                    positions.append((locations[i], float(pos[0]), float(pos[1])))
                else:
                    positions.append(None)
            self.log(f"Positions: {positions}")
            return positions  # type: ignore[return-value]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []

    def search_nearby(
        self, key: str, longitude: float, latitude: float, radius: float, unit: str = "km", count: int = 10
    ) -> list[str]:
        """Search for locations within radius.

        Args:
            key: The geo key.
            longitude: Center longitude.
            latitude: Center latitude.
            radius: Search radius.
            unit: Unit of measurement (km, mi, ft).
            count: Maximum number of results.

        Returns:
            List of location names.
        """
        try:
            results = self.redis_client.georadius(key, longitude, latitude, radius, unit=unit, count=count)
            self.log(f"Found {len(results)} locations within {radius} {unit}")
            return results
        except Exception as e:
            logger.error(f"Error searching nearby: {e}")
            return []

    def search_nearby_with_distance(
        self, key: str, longitude: float, latitude: float, radius: float, unit: str = "km", count: int = 10
    ) -> list[tuple[str, float]]:
        """Search for locations within radius with distance.

        Args:
            key: The geo key.
            longitude: Center longitude.
            latitude: Center latitude.
            radius: Search radius.
            unit: Unit of measurement (km, mi, ft).
            count: Maximum number of results.

        Returns:
            List of (location, distance) tuples.
        """
        try:
            results = self.redis_client.georadius(
                key, longitude, latitude, radius, unit=unit, count=count, withdist=True
            )
            self.log(f"Found {len(results)} locations with distances")
            return results
        except Exception as e:
            logger.error(f"Error searching nearby with distance: {e}")
            return []
