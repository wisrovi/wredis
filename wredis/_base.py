"""Base manager for all WRedis sync managers."""
from __future__ import annotations

from typing import Any

import redis
from loguru import logger

from wredis._exceptions import OperationError, ValidationError
from wredis._retry import retry
from wredis._validation import validate_key


class BaseManager:
    """Base class for all synchronous Redis managers.

    Provides connection pooling, health checks, validation, and retry logic.

    Attributes:
        redis_client: Redis client instance.
        verbose: Enables detailed logging if True.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        socket_timeout: float = 5.0,
        max_connections: int = 10,
        decode_responses: bool = False,
        verbose: bool = True,
    ):
        """Initialize the BaseManager.

        Args:
            host: Redis server hostname.
            port: Redis server port.
            db: Redis database number.
            password: Redis password (optional).
            socket_timeout: Socket timeout in seconds.
            max_connections: Maximum connections in pool.
            decode_responses: Decode responses to strings.
            verbose: Enable detailed logging.
        """
        self._pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_timeout,
            retry_on_timeout=True,
            max_connections=max_connections,
            decode_responses=decode_responses,
        )
        self.redis_client = redis.StrictRedis(connection_pool=self._pool)
        self.verbose = verbose

    def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled.

        Args:
            message: The message to log.
            level: The log level.
        """
        if self.verbose:
            getattr(logger, level)(message)

    def health_check(self) -> bool:
        """Check if Redis connection is alive.

        Returns:
            True if Redis is reachable.

        Raises:
            OperationError: If health check fails.
        """
        try:
            return self.redis_client.ping()
        except redis.RedisError as e:
            raise OperationError(f"Redis health check failed: {e}") from e

    @retry(max_attempts=3, delay=0.1, backoff=2.0)
    def _execute(self, operation: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a Redis operation with retry.

        Args:
            operation: Name of the Redis method to call.
            *args: Positional arguments for the operation.
            **kwargs: Keyword arguments for the operation.

        Returns:
            Result of the Redis operation.

        Raises:
            OperationError: If the operation fails after retries.
        """
        try:
            return getattr(self.redis_client, operation)(*args, **kwargs)
        except redis.RedisError as e:
            raise OperationError(f"Redis {operation} failed: {e}") from e

    def close(self) -> None:
        """Close the connection pool."""
        self._pool.disconnect()
        self.log("Connection pool closed")

    def __enter__(self) -> "BaseManager":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
