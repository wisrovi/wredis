"""Async Redis Pipeline Manager - batch command execution."""

from typing import Any

import redis.asyncio as redis
from loguru import logger


class AsyncRedisPipelineManager:
    """Manages Redis pipeline operations asynchronously.

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
        """Initialize the AsyncRedisPipelineManager."""
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.verbose = verbose

    async def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    async def execute_commands(self, commands: list[tuple[str, list[Any]]]) -> list[Any]:
        """Execute multiple commands in a pipeline."""
        try:
            pipe = self.redis_client.pipeline()
            for cmd, args in commands:
                getattr(pipe, cmd)(*args)
            results = await pipe.execute()
            await self.log(f"Executed {len(commands)} commands in pipeline")
            return results
        except Exception as e:
            logger.error(f"Error executing pipeline: {e}")
            return []

    async def set_get(self, key: str, value: str) -> str | None:
        """Set and get a value in one pipeline."""
        try:
            pipe = self.redis_client.pipeline()
            pipe.set(key, value)
            pipe.get(key)
            results = await pipe.execute()
            return results[1]
        except Exception as e:
            logger.error(f"Error in set_get pipeline: {e}")
            return None

    async def mget_pipeline(self, *keys: str) -> list[str | None]:
        """Get multiple keys in a pipeline."""
        try:
            pipe = self.redis_client.pipeline()
            for key in keys:
                pipe.get(key)
            results = await pipe.execute()
            return results
        except Exception as e:
            logger.error(f"Error in mget pipeline: {e}")
            return []

    async def mset_pipeline(self, mapping: dict[str, str]) -> bool:
        """Set multiple keys in a pipeline."""
        try:
            pipe = self.redis_client.pipeline()
            for key, value in mapping.items():
                pipe.set(key, value)
            await pipe.execute()
            await self.log(f"Set {len(mapping)} keys via pipeline")
            return True
        except Exception as e:
            logger.error(f"Error in mset pipeline: {e}")
            return False

    async def delete_keys(self, *keys: str) -> int:
        """Delete multiple keys in a pipeline."""
        try:
            pipe = self.redis_client.pipeline()
            for key in keys:
                pipe.delete(key)
            results = await pipe.execute()
            return sum(1 for r in results if r > 0)
        except Exception as e:
            logger.error(f"Error in delete pipeline: {e}")
            return 0
