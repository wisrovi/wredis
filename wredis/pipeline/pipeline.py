"""Redis Pipeline Manager - batch command execution."""

from typing import Any

import redis
from loguru import logger


class RedisPipelineManager:
    """Manages Redis pipeline operations.

    Attributes:
        redis_client: Redis client instance.
        verbose: Enables detailed logging if True.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        verbose: bool = True,
    ):
        """Initialize the RedisPipelineManager."""
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.verbose = verbose

    def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    def execute_commands(self, commands: list[tuple[str, list[Any]]]) -> list[Any]:
        """Execute multiple commands in a pipeline.

        Args:
            commands: List of (command_name, args) tuples.

        Returns:
            List of results in order.
        """
        try:
            pipe = self.redis_client.pipeline()
            for cmd, args in commands:
                getattr(pipe, cmd)(*args)
            results = pipe.execute()
            self.log(f"Executed {len(commands)} commands in pipeline")
            return results
        except Exception as e:
            logger.error(f"Error executing pipeline: {e}")
            return []

    def set_get(self, key: str, value: str) -> str | None:
        """Set and get a value in one pipeline.

        Args:
            key: Redis key.
            value: Value to set.

        Returns:
            The value (or None).
        """
        try:
            pipe = self.redis_client.pipeline()
            pipe.set(key, value)
            pipe.get(key)
            results = pipe.execute()
            return results[1]
        except Exception as e:
            logger.error(f"Error in set_get pipeline: {e}")
            return None

    def mget_pipeline(self, *keys: str) -> list[str | None]:
        """Get multiple keys in a pipeline.

        Args:
            keys: Redis keys.

        Returns:
            List of values.
        """
        try:
            pipe = self.redis_client.pipeline()
            for key in keys:
                pipe.get(key)
            results = pipe.execute()
            return results
        except Exception as e:
            logger.error(f"Error in mget pipeline: {e}")
            return []

    def mset_pipeline(self, mapping: dict[str, str]) -> bool:
        """Set multiple keys in a pipeline.

        Args:
            mapping: Dictionary of key-value pairs.

        Returns:
            True if successful.
        """
        try:
            pipe = self.redis_client.pipeline()
            for key, value in mapping.items():
                pipe.set(key, value)
            pipe.execute()
            self.log(f"Set {len(mapping)} keys via pipeline")
            return True
        except Exception as e:
            logger.error(f"Error in mset pipeline: {e}")
            return False

    def delete_keys(self, *keys: str) -> int:
        """Delete multiple keys in a pipeline.

        Args:
            keys: Redis keys to delete.

        Returns:
            Number of keys deleted.
        """
        try:
            pipe = self.redis_client.pipeline()
            for key in keys:
                pipe.delete(key)
            results = pipe.execute()
            return sum(1 for r in results if r > 0)
        except Exception as e:
            logger.error(f"Error in delete pipeline: {e}")
            return 0
