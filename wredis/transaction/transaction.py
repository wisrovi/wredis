"""Redis Transaction Manager - atomic operations with WATCH/MULTI/EXEC."""

from typing import Any

import redis
from loguru import logger


class RedisTransactionManager:
    """Manages Redis transaction operations.

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
        """Initialize the RedisTransactionManager."""
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.verbose = verbose

    def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    def execute_transaction(self, commands: list[tuple[str, list[Any]]]) -> list[Any] | None:
        """Execute multiple commands in a transaction.

        Args:
            commands: List of (command_name, args) tuples.

        Returns:
            List of results, or None on error.
        """
        try:
            pipe = self.redis_client.pipeline(transaction=True)
            for cmd, args in commands:
                getattr(pipe, cmd)(*args)
            results = pipe.execute()
            self.log(f"Executed {len(commands)} commands in transaction")
            return results
        except Exception as e:
            logger.error(f"Error executing transaction: {e}")
            return None

    def watch_and_execute(self, keys: list[str], commands: list[tuple[str, list[Any]]]) -> list[Any] | None:
        """Watch keys and execute transaction.

        Args:
            keys: Keys to watch for changes.
            commands: Commands to execute in transaction.

        Returns:
            List of results, or None if watched keys changed.
        """
        try:
            self.redis_client.watch(*keys)
            pipe = self.redis_client.pipeline(transaction=True)
            for cmd, args in commands:
                getattr(pipe, cmd)(*args)
            results = pipe.execute()
            self.log(f"Transaction executed successfully with WATCH on {keys}")
            return results
        except redis.WatchError:
            self.log("Transaction aborted - watched keys changed", level="warning")
            return None
        except Exception as e:
            logger.error(f"Error in watch_and_execute: {e}")
            return None
        finally:
            self.redis_client.unwatch()

    def set_if_not_exists(self, key: str, value: str, ttl: int = -1) -> bool:
        """Set a key only if it doesn't exist (atomic).

        Args:
            key: Redis key.
            value: Value to set.
            ttl: Optional TTL in seconds.

        Returns:
            True if set, False if key exists.
        """
        try:
            result = self.redis_client.set(key, value, nx=True, ex=ttl if ttl > 0 else None)
            self.log(f"SET NX result for '{key}': {result}")
            return result is not None
        except Exception as e:
            logger.error(f"Error in set_if_not_exists: {e}")
            return False

    def increment_atomic(self, key: str, amount: int = 1) -> int:
        """Atomically increment a counter.

        Args:
            key: Redis key.
            amount: Amount to increment by.

        Returns:
            New value.
        """
        try:
            result = self.redis_client.incrby(key, amount) if amount > 0 else self.redis_client.decrby(key, abs(amount))
            self.log(f"Incremented '{key}' to {result}")
            return result
        except Exception as e:
            logger.error(f"Error in increment_atomic: {e}")
            return 0

    def get_and_set(self, key: str, value: str) -> str | None:
        """Atomically get and set a value.

        Args:
            key: Redis key.
            value: New value.

        Returns:
            Old value.
        """
        try:
            pipe = self.redis_client.pipeline()
            pipe.get(key)
            pipe.set(key, value)
            results = pipe.execute()
            return results[0]
        except Exception as e:
            logger.error(f"Error in get_and_set: {e}")
            return None
