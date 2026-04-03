"""Async Redis Geo Manager - Geographic operations with Redis."""

from typing import Any

import redis.asyncio as redis
from loguru import logger


class AsyncRedisGeoManager:
    """Manages Redis geographic operations asynchronously.

    Attributes:
        redis_client: Async Redis client instance.
        verbose: Enables detailed logging if True.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        verbose: bool = True,
    ):
        """Initialize the AsyncRedisGeoManager."""
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.verbose = verbose

    async def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    async def add_location(self, key: str, location: str, longitude: float, latitude: float) -> None:
        """Add a location to a geo key."""
        try:
            await self.redis_client.geoadd(key, (longitude, latitude, location))
            await self.log(f"Added location '{location}' to key '{key}'")
        except Exception as e:
            logger.error(f"Error adding location to key '{key}': {e}")

    async def get_distance(self, key: str, location1: str, location2: str, unit: str = "km") -> float | None:
        """Get distance between two locations."""
        try:
            distance = await self.redis_client.geodist(key, location1, location2, unit=unit)
            await self.log(f"Distance between {location1} and {location2}: {distance} {unit}")
            return distance
        except Exception as e:
            logger.error(f"Error getting distance: {e}")
            return None

    async def get_positions(self, key: str, *locations: str) -> list[tuple[str, float, float] | None]:
        """Get positions of locations."""
        try:
            results = await self.redis_client.geopos(key, *locations)
            positions = []
            for i, pos in enumerate(results):
                if pos:
                    positions.append((locations[i], float(pos[0]), float(pos[1])))
                else:
                    positions.append(None)
            await self.log(f"Positions: {positions}")
            return positions  # type: ignore[return-value]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []

    async def search_nearby(
        self, key: str, longitude: float, latitude: float, radius: float, unit: str = "km", count: int = 10
    ) -> list[str]:
        """Search for locations within radius."""
        try:
            results = await self.redis_client.georadius(key, longitude, latitude, radius, unit=unit, count=count)
            await self.log(f"Found {len(results)} locations within {radius} {unit}")
            return results
        except Exception as e:
            logger.error(f"Error searching nearby: {e}")
            return []

    async def search_nearby_with_distance(
        self, key: str, longitude: float, latitude: float, radius: float, unit: str = "km", count: int = 10
    ) -> list[tuple[str, float]]:
        """Search for locations within radius with distance."""
        try:
            results = await self.redis_client.georadius(
                key, longitude, latitude, radius, unit=unit, count=count, withdist=True
            )
            await self.log(f"Found {len(results)} locations with distances")
            return results
        except Exception as e:
            logger.error(f"Error searching nearby with distance: {e}")
            return []
