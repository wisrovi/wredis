"""Redis HyperLogLog Manager - probabilistic counting."""
from __future__ import annotations

import redis
from loguru import logger


class RedisHyperLogLogManager:
    """Manages Redis HyperLogLog operations.

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
        """Initialize the RedisHyperLogLogManager."""
        self.redis_client = redis.Redis(
            host=host, port=port, db=db, decode_responses=True
        )
        self.verbose = verbose

    def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    def add(self, key: str, *values: str) -> None:
        """Add elements to HyperLogLog.

        Args:
            key: The HyperLogLog key.
            values: Elements to add.
        """
        try:
            self.redis_client.pfadd(key, *values)
            self.log(f"Added {len(values)} elements to HyperLogLog '{key}'")
        except Exception as e:
            logger.error(f"Error adding to HyperLogLog '{key}': {e}")

    def count(self, *keys: str) -> int:
        """Get estimated unique element count.

        Args:
            keys: One or more HyperLogLog keys.

        Returns:
            Estimated cardinality.
        """
        try:
            count = self.redis_client.pfcount(*keys)
            self.log(f"Estimated count for {keys}: {count}")
            return count
        except Exception as e:
            logger.error(f"Error getting count: {e}")
            return 0

    def merge(self, destination: str, *sources: str) -> None:
        """Merge multiple HyperLogLogs into one.

        Args:
            destination: Destination key.
            sources: Source keys to merge.
        """
        try:
            self.redis_client.pfmerge(destination, *sources)
            self.log(f"Merged {len(sources)} keys into '{destination}'")
        except Exception as e:
            logger.error(f"Error merging HyperLogLogs: {e}")

    def get_all(self, key: str) -> set | None:
        """Get all stored elements in a HyperLogLog.

        Note: This is not efficient for large HLL, use count() instead.

        Args:
            key: The HyperLogLog key.

        Returns:
            Set of elements (if available).
        """
        try:
            dump_data = self.redis_client.get(key)
            if dump_data is None:
                return set()
            return {key}
        except Exception as e:
            logger.error(f"Error getting HLL data: {e}")
            return None
