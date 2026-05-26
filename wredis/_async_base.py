"""Base manager for all WRedis async managers."""

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

        for attempt in range(max_attempts):
            try:
                return await getattr(self.redis_client, operation)(*args, **kwargs)
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
