"""Async Redis Bitmap Manager."""

import json

import redis.asyncio as redis
from loguru import logger


class AsyncRedisBitmapManager:
    """Manages Redis bitmap operations asynchronously.

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
        """Initialize the AsyncRedisBitmapManager.

        Args:
            host: Hostname of the Redis server.
            port: Port number of the Redis server.
            db: Redis database index.
            verbose: Enable detailed logging if True.
        """
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.verbose = verbose

    async def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled.

        Args:
            message: The message to log.
            level: The log level (e.g., "info", "warning", "error").
        """
        if self.verbose:
            getattr(logger, level)(message)

    async def set_bit(self, key: str, offset: int, value: int, ttl: int = -1) -> None:
        """Set a bit at a specific position in a bitmap.

        Args:
            key: The Redis key for the bitmap.
            offset: The position of the bit to set.
            value: The value to set the bit to (0 or 1).
            ttl: Time-to-live for the key in seconds. If -1, no TTL is set.
        """
        try:
            await self.redis_client.setbit(key, offset, value)
            await self.log(f"Set bit in '{key}' at position {offset} to value {value}.")

            if ttl > 0:
                await self.redis_client.expire(key, ttl)
                await self.log(f"Set TTL of {ttl} seconds for '{key}'.")
        except Exception as e:
            logger.error(f"Error setting bit in '{key}': {e}")

    async def get_bit(self, key: str, offset: int) -> int:
        """Retrieve the value of a bit at a specific position.

        Args:
            key: The Redis key for the bitmap.
            offset: The position of the bit to retrieve.

        Returns:
            The value of the bit (0 or 1).
        """
        try:
            bit_value = await self.redis_client.getbit(key, offset)
            await self.log(f"Bit value in '{key}' at position {offset}: {bit_value}.")
            return bit_value
        except Exception as e:
            logger.error(f"Error retrieving bit from '{key}': {e}")
            return 0

    async def count_bits(self, key: str) -> int:
        """Count the number of bits set to 1 in a bitmap.

        Args:
            key: The Redis key for the bitmap.

        Returns:
            The number of bits set to 1.
        """
        try:
            bit_count = await self.redis_client.bitcount(key)
            await self.log(f"Number of bits set to 1 in '{key}': {bit_count}.")
            return bit_count
        except Exception as e:
            logger.error(f"Error counting bits in '{key}': {e}")
            return 0

    async def get_ttl(self, key: str) -> int:
        """Retrieve the time-to-live (TTL) for a bitmap key.

        Args:
            key: The Redis key for the bitmap.

        Returns:
            The TTL in seconds. -1 if no TTL is set, -2 if the key does not exist.
        """
        try:
            ttl = await self.redis_client.ttl(key)
            if ttl == -1:
                await self.log(f"The bitmap '{key}' has no TTL set.", level="warning")
            elif ttl == -2:
                await self.log(f"The bitmap '{key}' does not exist.", level="warning")
            else:
                await self.log(f"The TTL for bitmap '{key}' is {ttl} seconds.")
            return ttl
        except Exception as e:
            logger.error(f"Error retrieving TTL for '{key}': {e}")
            return -2

    async def extend_ttl(self, key: str, ttl: int) -> None:
        """Extend or set a new TTL for a bitmap key.

        Args:
            key: The Redis key for the bitmap.
            ttl: The new TTL in seconds.
        """
        try:
            if await self.redis_client.exists(key):
                await self.redis_client.expire(key, ttl)
                await self.log(f"Extended TTL for bitmap '{key}' to {ttl} seconds.")
            else:
                await self.log(
                    f"Cannot set TTL because the bitmap '{key}' does not exist.",
                    level="warning",
                )
        except Exception as e:
            logger.error(f"Error extending TTL for '{key}': {e}")

    async def set_json(self, key: str, value: dict | list, ttl: int = -1) -> None:
        """Set a JSON value in Redis.

        Args:
            key: The Redis key.
            value: The value to serialize as JSON.
            ttl: Time-to-live in seconds.
        """
        try:
            json_value = json.dumps(value)
            await self.redis_client.set(key, json_value)
            await self.log(f"Set JSON value for key '{key}'.")

            if ttl > 0:
                await self.redis_client.expire(key, ttl)
                await self.log(f"Set TTL of {ttl} seconds for '{key}'.")
        except Exception as e:
            logger.error(f"Error setting JSON for key '{key}': {e}")

    async def get_json(self, key: str) -> dict | list | None:
        """Get and deserialize a JSON value from Redis.

        Args:
            key: The Redis key.

        Returns:
            The deserialized JSON value, or None if not found.
        """
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            await self.log(f"Key '{key}' does not exist.", level="warning")
            return None
        except Exception as e:
            logger.error(f"Error getting JSON for key '{key}': {e}")
            return None

    async def delete_key(self, key: str) -> bool:
        """Delete a key from Redis.

        Args:
            key: The Redis key to delete.

        Returns:
            True if the key was deleted, False otherwise.
        """
        try:
            result = await self.redis_client.delete(key)
            await self.log(f"Deleted key '{key}': {result > 0}")
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting key '{key}': {e}")
            return False
