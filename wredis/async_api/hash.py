"""Async Redis Hash Manager."""

from __future__ import annotations

import contextlib
import json

import redis.asyncio as redis
from loguru import logger


class AsyncRedisHashManager:
    """Manages Redis hash operations asynchronously.

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
        """Initialize the AsyncRedisHashManager.

        Args:
            host: Hostname of the Redis server.
            port: Port number of the Redis server.
            db: Redis database index.
            verbose: Enable detailed logging if True.
        """
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.verbose = verbose

    async def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    async def create_hash(self, hash_name: str, key: str, value: dict | str, ttl: int = -1) -> None:
        """Write a key-value pair into a Redis hash.

        Args:
            hash_name: Name of the hash in Redis.
            key: Key within the hash.
            value: Value to store, serialized to JSON if it is a dictionary.
            ttl: Time-to-live for the hash in seconds. If -1, no TTL is set.
        """
        try:
            json_value = json.dumps(value) if isinstance(value, dict) else value
            await self.redis_client.hset(hash_name, key, json_value)
            await self.log(f"Written to hash '{hash_name}' -> {key}: {value}")

            if ttl > 0:
                await self.redis_client.expire(hash_name, ttl)
                await self.log(f"Set TTL of {ttl} seconds for hash '{hash_name}'")
        except Exception as e:
            logger.error(f"Error writing to hash '{hash_name}': {e}")

    async def exist(self, hash_name: str) -> bool:
        """Checks if a Redis hash exists asynchronously.

        Args:
            hash_name (str): Name of the hash in Redis.

        Returns:
            bool: True if the hash exists, False otherwise.
        """
        try:
            result = await self.redis_client.exists(hash_name)
            exists = result > 0
            await self.log(f"Check existence of hash '{hash_name}': {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking existence of hash '{hash_name}': {e}")
            return False

    async def read_hash(self, hash_name: str, key: str) -> dict | str | None:
        """Read a key-value pair from a Redis hash.

        Args:
            hash_name: Name of the hash in Redis.
            key: Key within the hash.

        Returns:
            The value stored, deserialized from JSON if applicable, or None if not found.
        """
        try:
            json_value = await self.redis_client.hget(hash_name, key)
            if json_value:
                json_value = json_value.decode()
                try:
                    return json.loads(json_value)
                except json.JSONDecodeError:
                    return json_value
            else:
                await self.log(
                    f"Field '{key}' does not exist in hash '{hash_name}'.",
                    level="warning",
                )
                return None
        except Exception as e:
            logger.error(f"Error reading from hash '{hash_name}': {e}")
            return None

    async def update_hash(self, hash_name: str, key: str, new_data: dict) -> None:
        """Update a key-value pair in a Redis hash.

        Args:
            hash_name: Name of the hash in Redis.
            key: Key within the hash.
            new_data: New data to update the field.
        """
        try:
            current_value = await self.read_hash(hash_name, key)

            if isinstance(current_value, dict):
                current_value.update(new_data)
                await self.create_hash(hash_name, key, current_value)
                await self.log(f"Updated field '{key}' in hash '{hash_name}': {current_value}")
            else:
                await self.create_hash(hash_name, key, new_data)
                await self.log(f"Added new field '{key}' to hash '{hash_name}': {new_data}")
        except Exception as e:
            logger.error(f"Error updating field '{key}' in hash '{hash_name}': {e}")

    async def delete_hash_field(self, hash_name: str, key: str) -> None:
        """Delete a specific field from a Redis hash."""
        try:
            result = await self.redis_client.hdel(hash_name, key)
            if result:
                await self.log(f"Deleted field '{key}' from hash '{hash_name}'.")
            else:
                await self.log(
                    f"Field '{key}' does not exist in hash '{hash_name}'.",
                    level="warning",
                )
        except Exception as e:
            logger.error(f"Error deleting field '{key}' from hash '{hash_name}': {e}")

    async def read_all_hash(self, hash_name: str) -> dict | None:
        """Read all fields and values from a Redis hash."""
        try:
            hash_data = await self.redis_client.hgetall(hash_name)
            if hash_data:
                items = {}
                for k, v in hash_data.items():
                    value = v.decode()
                    with contextlib.suppress(json.JSONDecodeError):
                        value = json.loads(value)
                    items[k.decode()] = value

                await self.log(f"Read all fields from hash '{hash_name}': {items}")
                return items
            else:
                await self.log(f"Hash '{hash_name}' is empty or does not exist.", level="warning")
                return None
        except Exception as e:
            logger.error(f"Error reading all fields from hash '{hash_name}': {e}")
            return None

    async def get_ttl(self, hash_name: str) -> int | None:
        """Retrieve the remaining TTL for a Redis hash."""
        try:
            ttl = await self.redis_client.ttl(hash_name)
            if ttl == -1:
                await self.log(f"Hash '{hash_name}' has no TTL set.", level="warning")
            elif ttl == -2:
                await self.log(f"Hash '{hash_name}' does not exist.", level="warning")
            else:
                await self.log(f"TTL for hash '{hash_name}' is {ttl} seconds.")
            return ttl
        except Exception as e:
            logger.error(f"Error retrieving TTL for hash '{hash_name}': {e}")
            return None

    async def extend_ttl(self, hash_name: str, ttl: int) -> None:
        """Extend or set a new TTL for a Redis hash."""
        try:
            if await self.redis_client.exists(hash_name):
                await self.redis_client.expire(hash_name, ttl)
                await self.log(f"Extended TTL for hash '{hash_name}' to {ttl} seconds.")
            else:
                await self.log(
                    f"Cannot set TTL because hash '{hash_name}' does not exist.",
                    level="warning",
                )
        except Exception as e:
            logger.error(f"Error extending TTL for hash '{hash_name}': {e}")

    async def set_json(self, key: str, value: dict | list, ttl: int = -1) -> None:
        """Set a JSON value in Redis."""
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
