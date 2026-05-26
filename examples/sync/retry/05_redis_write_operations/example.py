"""Example 05: Retry with Redis write operations.

Demonstrates using @retry for SET/HSET operations that may
fail and need to be retried safely.
"""

import redis

from wredis._retry import retry


class RedisWriteMock:
    """Mock Redis client for write operations."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._attempts = 0

    def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self._attempts += 1
        if self._attempts <= 1:
            raise redis.TimeoutError("Write timeout expired")
        self._store[key] = value
        return True

    def get(self, key: str) -> str | None:
        return self._store.get(key)


client = RedisWriteMock()


@retry(max_attempts=3, delay=0.1, backoff=2.0)
def save_to_cache(key: str, value: str, ttl: int | None = None) -> bool:
    """Saves a key-value pair to Redis with retry."""
    return client.set(key, value, ex=ttl)


@retry(max_attempts=3, delay=0.1, backoff=2.0)
def save_hash(field: str, value: str) -> bool:
    """Saves data to a Redis hash with retry."""
    return client.set(f"hash:{field}", value)


if __name__ == "__main__":
    print("=== Example 05: Redis Write Operations ===")

    # Save with retry
    success = save_to_cache("config:theme", "dark", ttl=3600)
    print(f"Saved successfully: {success}")

    # Verify it was saved correctly
    value = client.get("config:theme")
    print(f"Stored value: {value}")

    # Save hash
    success_hash = save_hash("name", "WRedis")
    print(f"Hash saved: {success_hash}")
    print(f"Hash value: {client.get('hash:name')}")
