"""Async Redis HyperLogLog Manager - probabilistic counting."""

import redis.asyncio as redis
from loguru import logger


class AsyncRedisHyperLogLogManager:
    """Manages Redis HyperLogLog operations asynchronously.

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
        """Initialize the AsyncRedisHyperLogLogManager."""
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.verbose = verbose

    async def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    async def add(self, key: str, *values: str) -> None:
        """Add elements to HyperLogLog."""
        try:
            await self.redis_client.pfadd(key, *values)
            await self.log(f"Added {len(values)} elements to HyperLogLog '{key}'")
        except Exception as e:
            logger.error(f"Error adding to HyperLogLog '{key}': {e}")

    async def count(self, *keys: str) -> int:
        """Get estimated unique element count."""
        try:
            count = await self.redis_client.pfcount(*keys)
            await self.log(f"Estimated count for {keys}: {count}")
            return count
        except Exception as e:
            logger.error(f"Error getting count: {e}")
            return 0

    async def merge(self, destination: str, *sources: str) -> None:
        """Merge multiple HyperLogLogs into one."""
        try:
            await self.redis_client.pfmerge(destination, *sources)
            await self.log(f"Merged {len(sources)} keys into '{destination}'")
        except Exception as e:
            logger.error(f"Error merging HyperLogLogs: {e}")
