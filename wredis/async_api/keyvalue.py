"""Async Redis Key-Value Manager."""

from __future__ import annotations

import contextlib
import json
from typing import Any, Optional, Union

import redis.asyncio as redis
from loguru import logger


class AsyncRedisKeyValueManager:
    """Manages Redis key-value operations asynchronously for strings, binary, and JSON with TTL.

    Attributes:
        redis_client (redis.Redis): Async Redis client instance.
        verbose (bool): Enables detailed logging if True.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        verbose: bool = True,
    ):
        """Initializes AsyncRedisKeyValueManager with connection parameters.

        Args:
            host (str): Hostname of the Redis server.
            port (int): Port number of the Redis server.
            db (int): Redis database index.
            password (Optional[str]): Password for Redis authentication.
            verbose (bool): Enable detailed logging if True.
        """
        self.redis_client = redis.Redis(host=host, port=port, db=db, password=password)
        self.verbose = verbose

    async def log(self, message: str, level: str = "info") -> None:
        """Logs a message if verbose mode is enabled.

        Args:
            message (str): Message to log.
            level (str): Log level.
        """
        if self.verbose:
            getattr(logger, level)(message)

    async def set(
        self,
        key: str,
        value: Union[bytes, str, dict, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """Sets a key to a value asynchronously.

        Args:
            key (str): Redis key name.
            value (Union[bytes, str, dict, Any]): Binary bytes, string, or dictionary.
            ttl (Optional[int]): Time-to-live in seconds.

        Returns:
            bool: True if operation succeeded, False otherwise.
        """
        try:
            val_to_store: Union[bytes, str]
            if isinstance(value, (bytes, bytearray)):
                val_to_store = bytes(value)
            elif isinstance(value, dict):
                val_to_store = json.dumps(value)
            elif isinstance(value, str):
                val_to_store = value
            else:
                val_to_store = str(value)

            ex = ttl if (ttl is not None and ttl > 0) else None
            res = await self.redis_client.set(name=key, value=val_to_store, ex=ex)
            await self.log(f"Set key '{key}' (TTL={ttl})")
            return bool(res)
        except Exception as e:
            logger.error(f"Error setting key '{key}': {e}")
            return False

    async def setex(
        self, key: str, ttl: int, value: Union[bytes, str, dict, Any]
    ) -> bool:
        """Sets a key with expiration asynchronously.

        Args:
            key (str): Redis key name.
            ttl (int): Time-to-live in seconds.
            value (Union[bytes, str, dict, Any]): Value to store.

        Returns:
            bool: True if operation succeeded, False otherwise.
        """
        return await self.set(key=key, value=value, ttl=ttl)

    async def get(self, key: str) -> Optional[Union[bytes, str, dict, Any]]:
        """Gets the value of a key asynchronously.

        Args:
            key (str): Redis key name.

        Returns:
            Optional[Union[bytes, str, dict, Any]]: Stored value or None if missing/expired.
        """
        try:
            val = await self.redis_client.get(key)
            if val is None:
                return None
            if isinstance(val, bytes):
                try:
                    text = val.decode("utf-8")
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        return text
                except UnicodeDecodeError:
                    return val
            return val
        except Exception as e:
            logger.error(f"Error reading key '{key}': {e}")
            return None

    async def get_bytes(self, key: str) -> Optional[bytes]:
        """Gets raw binary bytes of a key asynchronously.

        Args:
            key (str): Redis key name.

        Returns:
            Optional[bytes]: Raw binary bytes or None.
        """
        try:
            val = await self.redis_client.get(key)
            if val is None:
                return None
            if isinstance(val, bytes):
                return val
            if isinstance(val, str):
                return val.encode("utf-8")
            return bytes(val)
        except Exception as e:
            logger.error(f"Error reading raw bytes for key '{key}': {e}")
            return None

    async def delete(self, key: str) -> bool:
        """Deletes a key asynchronously.

        Args:
            key (str): Redis key name.

        Returns:
            bool: True if key was deleted, False otherwise.
        """
        try:
            res = await self.redis_client.delete(key)
            await self.log(f"Deleted key '{key}'")
            return bool(res > 0)
        except Exception as e:
            logger.error(f"Error deleting key '{key}': {e}")
            return False

    async def exist(self, key: str) -> bool:
        """Checks if a key exists asynchronously.

        Args:
            key (str): Redis key name.

        Returns:
            bool: True if key exists, False otherwise.
        """
        try:
            res = await self.redis_client.exists(key)
            exists = bool(res > 0)
            await self.log(f"Checked existence of key '{key}': {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking existence of key '{key}': {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Alias for exist."""
        return await self.exist(key)

    async def close(self) -> None:
        """Closes the async connection."""
        with contextlib.suppress(Exception):
            await self.redis_client.aclose()
