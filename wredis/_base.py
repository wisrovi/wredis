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

    def exist(self, key: str) -> bool:
        """Check if a key exists in Redis.

        Args:
            key: The key to check.

        Returns:
            True if key exists, False otherwise.
        """
        try:
            result = self.redis_client.exists(key)
            exists = result > 0
            self.log(f"Check existence of key '{key}': {exists}")
            return exists
        except redis.RedisError as e:
            raise OperationError(f"Redis exists failed: {e}") from e

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
            # Handle common aliases
            if operation == "push":
                operation = "rpush"

            result = getattr(self.redis_client, operation)(*args, **kwargs)

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
        except redis.RedisError as e:
            raise OperationError(f"Redis {operation} failed: {e}") from e

    def close(self) -> None:
        """Close the connection pool."""
        self._pool.disconnect()
        self.log("Connection pool closed")

    def __enter__(self) -> BaseManager:
        """Enter the runtime context related to this object.

        Returns:
            The BaseManager instance.
        """
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the runtime context and close the connection pool.

        Args:
            exc_type: The exception type.
            exc_val: The exception value.
            exc_tb: The traceback.
        """
        self.close()
