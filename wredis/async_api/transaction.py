"""Async Redis Transaction Manager - atomic operations with WATCH/MULTI/EXEC."""

from typing import Any

import redis.asyncio as redis
from loguru import logger


class AsyncRedisTransactionManager:
    """Manages Redis transaction operations asynchronously.

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
        """Initialize the AsyncRedisTransactionManager."""
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.verbose = verbose

    async def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    async def execute_transaction(
        self, commands: list[tuple[str, list[Any]]]
    ) -> list[Any] | None:
        """Execute multiple commands in a transaction."""
        try:
            pipe = self.redis_client.pipeline(transaction=True)
            for cmd, args in commands:
                getattr(pipe, cmd)(*args)
            results = await pipe.execute()
            await self.log(f"Executed {len(commands)} commands in transaction")
            return results
        except Exception as e:
            logger.error(f"Error executing transaction: {e}")
            return None

    async def set_if_not_exists(self, key: str, value: str, ttl: int = -1) -> bool:
        """Set a key only if it doesn't exist (atomic)."""
        try:
            result = await self.redis_client.set(
                key, value, nx=True, ex=ttl if ttl > 0 else None
            )
            await self.log(f"SET NX result for '{key}': {result}")
            return result is not None
        except Exception as e:
            logger.error(f"Error in set_if_not_exists: {e}")
            return False

    async def increment_atomic(self, key: str, amount: int = 1) -> int:
        """Atomically increment a counter."""
        try:
            if amount > 0:
                result = await self.redis_client.incrby(key, amount)
            else:
                result = await self.redis_client.decrby(key, abs(amount))
            await self.log(f"Incremented '{key}' to {result}")
            return result
        except Exception as e:
            logger.error(f"Error in increment_atomic: {e}")
            return 0

    async def get_and_set(self, key: str, value: str) -> str | None:
        """Atomically get and set a value."""
        try:
            pipe = self.redis_client.pipeline()
            pipe.get(key)
            pipe.set(key, value)
            results = await pipe.execute()
            return results[0]
        except Exception as e:
            logger.error(f"Error in get_and_set: {e}")
            return None
