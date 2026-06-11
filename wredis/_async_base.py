"""Async base manager for Redis operations."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import redis.asyncio as aredis
from loguru import logger

from ._exceptions import OperationError


class AsyncBaseManager:
    """Base class for async Redis managers.

    Handles connection pooling and common operations like health checks.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        max_connections: int = 10,
        verbose: bool = True,
        **kwargs: Any,
    ):
        """Initialize the AsyncBaseManager.

        Args:
            host: Redis host.
            port: Redis port.
            db: Redis database index.
            max_connections: Maximum number of connections in the pool.
            verbose: Enable verbose logging.
            **kwargs: Additional arguments for aredis.Redis.
        """
        self.redis_client = aredis.Redis(
            host=host,
            port=port,
            db=db,
            max_connections=max_connections,
            **kwargs,
        )
        self.verbose = verbose

    async def __aenter__(self) -> AsyncBaseManager:
        """Async context manager entry.

        Returns:
            Self instance.
        """
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit.

        Closes the Redis connection pool.

        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Traceback.
        """
        await self.close()

    async def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled.

        Args:
            message: Message to log.
            level: Logging level.
        """
        if self.verbose:
            getattr(logger, level)(message)

    async def health_check(self) -> bool:
        """Check if Redis connection is alive.

        Returns:
            True if Redis is reachable.
        """
        try:
            return await self.redis_client.ping()
        except aredis.RedisError as e:
            await self.log(f"Health check failed: {e}", level="error")
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis.

        Args:
            key: Redis key to check.

        Returns:
            True if key exists, False otherwise.
        """
        try:
            result = await self.redis_client.exists(key)
            exists = result > 0
            await self.log(f"Check existence of key '{key}': {exists}")
            return exists
        except aredis.RedisError as e:
            raise OperationError(f"Redis exists failed: {e}") from e

    async def _execute(self, operation: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a Redis operation with retry.

        Args:
            operation: Name of the Redis method to call.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Result of the Redis operation.
        """
        max_attempts = 3
        delay = 0.1
        backoff = 2.0
        last_exception: Exception | None = None

        # Handle common aliases
        if operation == "push":
            operation = "rpush"

        for attempt in range(max_attempts):
            try:
                result = await getattr(self.redis_client, operation)(*args, **kwargs)

                # Auto-decode for convenience while preserving binary data
                if isinstance(result, bytes):
                    try:
                        return result.decode("utf-8")
                    except UnicodeDecodeError:
                        return result
                if isinstance(result, list):
                    decoded_list = []
                    for item in result:
                        if isinstance(item, bytes):
                            try:
                                decoded_list.append(item.decode("utf-8"))
                            except UnicodeDecodeError:
                                decoded_list.append(item)
                        else:
                            decoded_list.append(item)
                    return decoded_list
                if isinstance(result, dict):
                    decoded_dict: dict[str, Any] = {}
                    for k, v in result.items():
                        dk = k.decode("utf-8") if isinstance(k, bytes) else k
                        dv: Any = v
                        if isinstance(v, bytes):
                            try:
                                dv = v.decode("utf-8")
                            except UnicodeDecodeError:
                                pass
                        decoded_dict[dk] = dv
                    return decoded_dict

                return result
            except aredis.RedisError as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    await asyncio.sleep(delay * (backoff**attempt))

        raise OperationError(f"Redis {operation} failed after {max_attempts} attempts: {last_exception}")

    async def close(self) -> None:
        """Close the Redis connection pool."""
        await self.redis_client.close()
        await self.log("Connection closed")
