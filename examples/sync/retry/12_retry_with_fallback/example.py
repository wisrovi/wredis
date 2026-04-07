"""Example 12: Retry with local cache as fallback.

Implements a pattern where if Redis fails after all retries,
a local cache is used as fallback.
"""

import redis

from wredis._exceptions import OperationError
from wredis._retry import retry


class CacheWithFallback:
    """Cache that uses Redis with fallback to local memory."""

    def __init__(self) -> None:
        self._local_cache: dict[str, str] = {"config:app": "v1.0"}
        self._redis_attempts = 0

    def _read_redis(self, key: str) -> str | None:
        """Simulates Redis read (always fails)."""
        self._redis_attempts += 1
        raise redis.ConnectionError("Redis unavailable")

    @retry(max_attempts=3, delay=0.05, backoff=1.0)
    def get_with_retry(self, key: str) -> str | None:
        """Attempts to read from Redis with retries."""
        return self._read_redis(key)

    def get(self, key: str) -> str | None:
        """Gets data from Redis or fallback to local cache."""
        try:
            return self.get_with_retry(key)
        except OperationError:
            print(f"  [FALLBACK] Redis failed, using local cache for '{key}'")
            return self._local_cache.get(key)


cache = CacheWithFallback()


if __name__ == "__main__":
    print("=== Example 12: Cache with Fallback ===")

    # Key that exists in local cache
    value = cache.get("config:app")
    print(f"Value obtained: {value}")

    # Key that doesn't exist anywhere
    missing_value = cache.get("config:nonexistent")
    print(f"Non-existent value: {missing_value}")

    print(f"Total attempts to Redis: {cache._redis_attempts}")
