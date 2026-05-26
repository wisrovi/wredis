"""Example 10: Retry with wrapper decorator.

Shows how to create a custom decorator that combines @retry
with additional logic like input validation.
"""

import redis

from wredis._exceptions import OperationError
from wredis._retry import retry


def retry_with_validation(
    max_attempts: int = 3,
    delay: float = 0.1,
    backoff: float = 2.0,
):
    """Decorator that combines input validation with retry.

    First validates that arguments are correct, then applies
    automatic retry in case of Redis failures.
    """

    def decorator(func):
        @retry(max_attempts=max_attempts, delay=delay, backoff=backoff)
        def wrapper(*args, **kwargs):
            # Validation before execution
            if args and isinstance(args[0], str) and not args[0].strip():
                raise ValueError("Argument cannot be empty")
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Simulating a Redis service
class RedisService:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._attempts = 0

    def save(self, key: str, value: str) -> bool:
        self._attempts += 1
        if self._attempts <= 1:
            raise redis.TimeoutError("Write timeout")
        self._data[key] = value
        return True

    def get(self, key: str) -> str | None:
        return self._data.get(key)


service = RedisService()


@retry_with_validation(max_attempts=3, delay=0.1, backoff=1.5)
def save_data(key: str, value: str) -> bool:
    """Saves data with prior validation and retry."""
    return service.save(key, value)


@retry_with_validation(max_attempts=3, delay=0.1, backoff=1.5)
def fetch_data(key: str) -> str | None:
    """Fetches data with prior validation and retry."""
    return service.get(key)


if __name__ == "__main__":
    print("=== Example 10: Wrapper Decorator ===")

    # Successful operation with retry
    success = save_data("user:1", "Carlos")
    print(f"Saved: {success}")

    # Read without failures
    value = fetch_data("user:1")
    print(f"Value found: {value}")

    # Validation: empty key
    try:
        save_data("", "value")
    except ValueError as e:
        print(f"Validation detected error: {e}")

    print(f"Total service attempts: {service._attempts}")
