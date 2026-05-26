"""Async Redis Sorted Set Manager."""
from __future__ import annotations

import redis.asyncio as redis
from loguru import logger


class AsyncRedisSortedSetManager:
    """Manages Redis sorted sets asynchronously.

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
        """Initialize the AsyncRedisSortedSetManager."""
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.verbose = verbose

    async def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    async def add_to_sorted_set(
        self, key: str, score: float, member: str, ttl: int = -1
    ) -> None:
        """Add an element to the sorted set with its score."""
        try:
            await self.redis_client.zadd(key, {member: score})
            await self.log(f"Added to sorted set '{key}': {member} with score {score}")

            if ttl > 0:
                await self.redis_client.expire(key, ttl)
                await self.log(f"Set TTL of {ttl} seconds for sorted set '{key}'")
        except Exception as e:
            logger.error(f"Error adding to sorted set '{key}': {e}")

    async def get_sorted_set(
        self, key: str, start: int = 0, stop: int = -1, with_scores: bool = False
    ) -> list[str] | list[tuple[str, float]]:
        """Retrieve elements from the sorted set in a given range."""
        try:
            result = await self.redis_client.zrange(
                key, start, stop, withscores=with_scores
            )

            if with_scores:
                result = [(member.decode(), score) for member, score in result]
            else:
                result = [member.decode() for member in result]

            await self.log(f"Retrieved elements from sorted set '{key}': {result}")
            return result
        except Exception as e:
            logger.error(f"Error retrieving elements from sorted set '{key}': {e}")
            return []

    async def get_sorted_set_reverse(
        self, key: str, start: int = 0, stop: int = -1, with_scores: bool = False
    ) -> list[str] | list[tuple[str, float]]:
        """Retrieve elements from the sorted set in reverse order."""
        try:
            result = await self.redis_client.zrevrange(
                key, start, stop, withscores=with_scores
            )
            if with_scores:
                result = [(member.decode(), score) for member, score in result]
            else:
                result = [member.decode() for member in result]

            await self.log(
                f"Retrieved elements in reverse order from sorted set '{key}': {result}"
            )
            return result
        except Exception as e:
            logger.error(
                f"Error retrieving elements in reverse from sorted set '{key}': {e}"
            )
            return []

    async def remove_from_sorted_set(self, key: str, member: str) -> None:
        """Remove a member from the sorted set."""
        try:
            await self.redis_client.zrem(key, member)
            await self.log(f"Removed from sorted set '{key}': {member}")
        except Exception as e:
            logger.error(f"Error removing from sorted set '{key}': {e}")

    async def get_rank(self, key: str, member: str) -> int | None:
        """Retrieve the rank of a member."""
        try:
            rank = await self.redis_client.zrank(key, member)
            await self.log(f"Rank of '{member}' in sorted set '{key}': {rank}")
            return rank
        except Exception as e:
            logger.error(
                f"Error retrieving rank of '{member}' in sorted set '{key}': {e}"
            )
            return None

    async def get_score(self, key: str, member: str) -> float | None:
        """Retrieve the score of a member."""
        try:
            score = await self.redis_client.zscore(key, member)
            await self.log(f"Score of '{member}' in sorted set '{key}': {score}")
            return score
        except Exception as e:
            logger.error(
                f"Error retrieving score of '{member}' in sorted set '{key}': {e}"
            )
            return None

    async def delete_sorted_set(self, key: str) -> None:
        """Delete the entire sorted set."""
        try:
            await self.redis_client.delete(key)
            await self.log(f"Deleted entire sorted set '{key}'")
        except Exception as e:
            logger.error(f"Error deleting sorted set '{key}': {e}")

    async def set_ttl(self, key: str, ttl: int) -> None:
        """Set a TTL for an existing sorted set."""
        try:
            if await self.redis_client.exists(key):
                await self.redis_client.expire(key, ttl)
                await self.log(f"Set TTL of {ttl} seconds for sorted set '{key}'")
            else:
                logger.warning(f"Sorted set '{key}' does not exist to set TTL.")
        except Exception as e:
            logger.error(f"Error setting TTL for sorted set '{key}': {e}")

    async def get_ttl(self, key: str) -> int | None:
        """Retrieve the remaining TTL of a sorted set."""
        try:
            ttl = await self.redis_client.ttl(key)
            if ttl == -1:
                await self.log(f"Sorted set '{key}' has no TTL set.", level="warning")
            elif ttl == -2:
                await self.log(f"Sorted set '{key}' does not exist.", level="warning")
            else:
                await self.log(f"TTL for sorted set '{key}' is {ttl} seconds.")
            return ttl
        except Exception as e:
            logger.error(f"Error retrieving TTL for sorted set '{key}': {e}")
            return None

    async def increment_score(self, key: str, increment: float, member: str) -> None:
        """Increment the score of a member."""
        try:
            await self.redis_client.zincrby(key, increment, member)
            await self.log(
                f"Incremented score of '{member}' by {increment} in sorted set '{key}'"
            )
        except Exception as e:
            logger.error(
                f"Error incrementing score of '{member}' in sorted set '{key}': {e}"
            )

    async def get_sorted_set_by_score(
        self, key: str, min_score: float, max_score: float, with_scores: bool = False
    ) -> list[str] | list[tuple[str, float]]:
        """Retrieve members within a specific score range."""
        try:
            result = await self.redis_client.zrangebyscore(
                key, min_score, max_score, withscores=with_scores
            )
            if with_scores:
                result = [(member.decode(), score) for member, score in result]
            else:
                result = [member.decode() for member in result]
            await self.log(
                f"Retrieved elements by score from sorted set '{key}': {result}"
            )
            return result
        except Exception as e:
            logger.error(
                f"Error retrieving elements by score from sorted set '{key}': {e}"
            )
            return []

    async def set_json(self, key: str, value: dict | list, ttl: int = -1) -> None:
        """Set a JSON value in Redis."""
        import json

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
        import json

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
