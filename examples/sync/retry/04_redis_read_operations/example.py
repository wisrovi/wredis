"""Example 04: Retry with Redis read operations.

Shows how to use @retry for Redis GET operations that may fail
due to temporary connection issues.
"""

import redis

from wredis._retry import retry


# Simulating a Redis client that fails the first few times
class RedisMock:
    """Mock Redis client for demonstration."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {"user:1": "John", "user:2": "Mary"}
        self._attempts = 0

    def get(self, key: str) -> str | None:
        self._attempts += 1
        if self._attempts <= 2:
            raise redis.ConnectionError("Connection temporarily lost")
        return self._data.get(key)

    @property
    def attempts(self) -> int:
        return self._attempts


client = RedisMock()


@retry(max_attempts=3, delay=0.1, backoff=1.5)
def get_value(key: str) -> str | None:
    """Gets a value from Redis with automatic retry."""
    return client.get(key)


if __name__ == "__main__":
    print("=== Example 04: Redis Read Operations ===")

    value = get_value("user:1")
    print(f"Value obtained for 'user:1': {value}")
    print(f"Attempts needed: {client.attempts}")

    # Test with non-existent key
    client._attempts = 0
    nonexistent_value = get_value("user:99")
    print(f"Value for 'user:99': {nonexistent_value}")
