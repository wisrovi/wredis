"""Async Redis Set Manager."""
from __future__ import annotations

import redis.asyncio as redis
from loguru import logger


class AsyncRedisSetManager:
    """Manages Redis set operations asynchronously.

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
        """Initialize the AsyncRedisSetManager."""
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.verbose = verbose

    async def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    async def add_to_set(self, key: str, *values: str, ttl: int = -1) -> None:
        """Add one or more elements to a set."""
        try:
            await self.redis_client.sadd(key, *values)
            await self.log(f"Added to set '{key}': {values}")

            if ttl > 0:
                await self.redis_client.expire(key, ttl)
                await self.log(f"Set TTL of {ttl} seconds for set '{key}'")
        except Exception as e:
            logger.error(f"Error adding to set '{key}': {e}")

    async def get_set_members(self, key: str) -> set:
        """Retrieve all members of a set."""
        try:
            members = {
                member.decode() for member in await self.redis_client.smembers(key)
            }
            await self.log(f"Members of set '{key}': {members}")
            return members
        except Exception as e:
            logger.error(f"Error retrieving members of set '{key}': {e}")
            return set()

    async def is_member(self, key: str, value: str) -> bool:
        """Check if an element is a member of the set."""
        try:
            result = await self.redis_client.sismember(key, value)
            await self.log(
                f"Element '{value}' {'is' if result else 'is not'} a member of set '{key}'"
            )
            return result
        except Exception as e:
            logger.error(f"Error checking membership in set '{key}': {e}")
            return False

    async def remove_from_set(self, key: str, *values: str) -> None:
        """Remove one or more elements from a set."""
        try:
            await self.redis_client.srem(key, *values)
            await self.log(f"Removed from set '{key}': {values}")
        except Exception as e:
            logger.error(f"Error removing from set '{key}': {e}")

    async def get_ttl(self, key: str) -> int | None:
        """Retrieve the TTL of a set."""
        try:
            ttl = await self.redis_client.ttl(key)
            if ttl == -1:
                await self.log(f"Set '{key}' has no TTL set.", level="warning")
            elif ttl == -2:
                await self.log(f"Set '{key}' does not exist.", level="warning")
            else:
                await self.log(f"TTL for set '{key}' is {ttl} seconds.")
            return ttl
        except Exception as e:
            logger.error(f"Error retrieving TTL for set '{key}': {e}")
            return None

    async def extend_ttl(self, key: str, ttl: int) -> None:
        """Extend or set a new TTL for the set."""
        try:
            if await self.redis_client.exists(key):
                await self.redis_client.expire(key, ttl)
                await self.log(f"Extended TTL for set '{key}' to {ttl} seconds.")
            else:
                await self.log(
                    f"Cannot set TTL because set '{key}' does not exist.",
                    level="warning",
                )
        except Exception as e:
            logger.error(f"Error extending TTL for set '{key}': {e}")

    async def set_json(self, key: str, value: dict | list, ttl: int = -1) -> None:
        """Set a JSON value in Redis."""
        import json

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
        """Get and deserialize a JSON value from Redis."""
        import json

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting JSON for key '{key}': {e}")
            return None

    async def delete_key(self, key: str) -> bool:
        """Delete a key from Redis."""
        try:
            result = await self.redis_client.delete(key)
            await self.log(f"Deleted key '{key}': {result > 0}")
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting key '{key}': {e}")
            return False
