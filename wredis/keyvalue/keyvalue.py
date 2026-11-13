"""Redis key-value management implementation."""

from __future__ import annotations

import contextlib
import json
from typing import Any, Optional, Union

import redis
from loguru import logger


class RedisKeyValueManager:
    """Manages Redis direct key-value operations for strings, binary payloads, and JSON with TTL.

    Attributes:
        redis_client (redis.StrictRedis): Redis client instance.
        verbose (bool): Enables detailed logging if True.
        forensic (bool): Enables automatic forensic audit logging if True.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        verbose: bool = True,
        forensic: bool = False,
        connection_pool: Optional[redis.ConnectionPool] = None,
    ):
        """Initializes the RedisKeyValueManager with connection details.

        Args:
            host (str): Hostname of the Redis server.
            port (int): Port number of the Redis server.
            db (int): Redis database index.
            password (Optional[str]): Password for Redis authentication.
            verbose (bool): Enable detailed logging if True.
            forensic (bool): Enables automatic forensic audit logging if True.
            connection_pool (Optional[redis.ConnectionPool]): Custom connection pool.
        """
        if connection_pool is not None:
            self.redis_client = redis.StrictRedis(connection_pool=connection_pool)
        else:
            self.redis_client = redis.StrictRedis(
                host=host, port=port, db=db, password=password
            )
        self.verbose = verbose
        self.forensic = forensic

    def log(self, message: str, level: str = "info") -> None:
        """Logs a message if verbose mode is enabled.

        Args:
            message (str): Message to log.
            level (str): Log level.
        """
        if self.verbose:
            getattr(logger, level)(message)

    def set(
        self,
        key: str,
        value: Union[bytes, str, dict, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """Sets a key to a given value, optionally with a TTL in seconds.

        Args:
            key (str): Redis key name.
            value (Union[bytes, str, dict, Any]): Binary bytes, string, or dictionary.
            ttl (Optional[int]): Time-to-live in seconds. If None or <= 0, persists indefinitely.

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
            res = self.redis_client.set(name=key, value=val_to_store, ex=ex)

            if self.forensic:
                from wredis.forensic import record_forensic_entry

                val_audit = (
                    value if isinstance(value, dict) else {key: str(value)[:100]}
                )
                record_forensic_entry(
                    self.redis_client, key, "SET", before=None, after=val_audit
                )

            self.log(f"Set key '{key}' (TTL={ttl})")
            return bool(res)
        except Exception as e:
            logger.error(f"Error setting key '{key}': {e}")
            return False

    def setex(self, key: str, ttl: int, value: Union[bytes, str, dict, Any]) -> bool:
        """Sets a key to a value with explicit expiration in seconds.

        Args:
            key (str): Redis key name.
            ttl (int): Time-to-live in seconds.
            value (Union[bytes, str, dict, Any]): Value to store.

        Returns:
            bool: True if operation succeeded, False otherwise.
        """
        return self.set(key=key, value=value, ttl=ttl)

    def get(self, key: str) -> Optional[Union[bytes, str, dict, Any]]:
        """Gets the value of a key. Preserves binary bytes or parses UTF-8 JSON/string.

        Args:
            key (str): Redis key name.

        Returns:
            Optional[Union[bytes, str, dict, Any]]: Stored value or None if missing/expired.
        """
        try:
            val = self.redis_client.get(key)
            if val is None:
                self.log(f"Key '{key}' not found or expired", level="debug")
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

    def get_bytes(self, key: str) -> Optional[bytes]:
        """Gets the raw binary bytes of a key without any decoding or parsing.

        Args:
            key (str): Redis key name.

        Returns:
            Optional[bytes]: Raw binary bytes or None if missing/expired.
        """
        try:
            val = self.redis_client.get(key)
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

    def delete(self, key: str) -> bool:
        """Deletes a key from Redis.

        Args:
            key (str): Redis key name.

        Returns:
            bool: True if key was deleted, False otherwise.
        """
        try:
            res = self.redis_client.delete(key)
            self.log(f"Deleted key '{key}'")
            return bool(res > 0)
        except Exception as e:
            logger.error(f"Error deleting key '{key}': {e}")
            return False

    def exist(self, key: str) -> bool:
        """Checks if a key exists in Redis.

        Args:
            key (str): Redis key name.

        Returns:
            bool: True if key exists, False otherwise.
        """
        try:
            res = self.redis_client.exists(key)
            exists = bool(res > 0)
            self.log(f"Checked existence of key '{key}': {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking existence of key '{key}': {e}")
            return False

    def exists(self, key: str) -> bool:
        """Alias for exist.

        Args:
            key (str): Redis key name.

        Returns:
            bool: True if key exists, False otherwise.
        """
        return self.exist(key)

    def close(self) -> None:
        """Closes the Redis connection."""
        with contextlib.suppress(Exception):
            self.redis_client.close()
