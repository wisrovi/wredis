"""Base manager for all WRedis async managers."""
from __future__ import annotations

import asyncio
from typing import Any

import redis.asyncio as aredis
from loguru import logger

from wredis._exceptions import OperationError


class AsyncBaseManager:
    """Base class for all asynchronous Redis managers.

    Provides connection pooling, health checks, and retry logic.

    Attributes:
        redis_client: Async Redis client instance.
        verbose: Enables detailed logging if True.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        ssl: bool = False,
        socket_timeout: float = 5.0,
        max_connections: int = 10,
        decode_responses: bool = False,
        verbose: bool = True,
    ):
        """Initialize the AsyncBaseManager.

        Args:
            host: Redis server hostname.
            port: Redis server port.
            db: Redis database number.
            password: Redis password (optional).
            ssl: Enable SSL.
            socket_timeout: Socket timeout in seconds.
            max_connections: Maximum connections in pool.
            decode_responses: Decode responses to strings.
            verbose: Enable detailed logging.
        """
        # Create client directly - this works better with redis 7.0+
        self.redis_client = aredis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            ssl=ssl,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_timeout,
            retry_on_timeout=True,
            decode_responses=decode_responses,
            max_connections=max_connections,
        )
        self.verbose = verbose

    def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    async def health_check(self) -> bool:
        """Check if Redis connection is alive.

        Returns:
            True if Redis is reachable.

        Raises:
            OperationError: If health check fails.
        """
        try:
            return await self.redis_client.ping()
        except aredis.RedisError as e:
            raise OperationError(f"Redis health check failed: {e}") from e

    async def exist(self, key: str) -> bool:
        """Check if a key exists in Redis.

        Args:
            key: The key to check.

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
                    decoded_dict = {}
                    for k, v in result.items():
                        dk = k.decode("utf-8") if isinstance(k, bytes) else k
                        if isinstance(v, bytes):
                            try:
                                dv = v.decode("utf-8")
                            except UnicodeDecodeError:
                                dv = v
                        else:
                            dv = v
                        decoded_dict[dk] = dv
                    return decoded_dict
                    
                return result
            except aredis.RedisError as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    await asyncio.sleep(delay * (backoff**attempt))

        raise OperationError(
            f"Redis {operation} failed after {max_attempts} attempts: {last_exception}"
        ) from last_exception

    async def close(self) -> None:
        """Close the Redis connection."""
        await self.redis_client.aclose()
        self.log("Connection closed")

    async def __aenter__(self) -> "AsyncBaseManager":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
