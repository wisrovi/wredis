"""Automatic retry on specific errors demonstration.

Implements a retry decorator that only retries on
certain types of WRedis exceptions.
"""

import random
import time

from wredis._exceptions import OperationError, RedisConnectionError, ValidationError, WRedisError


def retry(max_attempts=3, wait=0.1, retryable_exceptions=None):
    """Decorator to retry functions on specific errors.

    Args:
        max_attempts: Maximum number of attempts.
        wait: Seconds between retries.
        retryable_exceptions: Tuple of exceptions that trigger
            retries. Default: (RedisConnectionError, OperationError).

    Returns:
        Decorator.
    """
    if retryable_exceptions is None:
        retryable_exceptions = (RedisConnectionError, OperationError)

    def decorator(func):
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as exc:
                    last_error = exc
                    print(f"  [{func.__name__}] Attempt {attempt}/{max_attempts} failed: {type(exc).__name__}: {exc}")
                    if attempt < max_attempts:
                        time.sleep(wait)
                except WRedisError as exc:
                    # Non-retryable errors are propagated immediately
                    print(f"  [{func.__name__}] Non-retryable error: {type(exc).__name__}: {exc}")
                    raise
            raise last_error

        return wrapper

    return decorator


# Simulate an unstable Redis client
class UnstableRedis:
    """Redis client that fails randomly."""

    def __init__(self):
        self._data = {}
        self._fail_rate = 0.7  # 70% failure probability

    def get(self, key):
        if random.random() < self._fail_rate:
            raise RedisConnectionError(f"Connection lost during GET '{key}'")
        return self._data.get(key)

    def set(self, key, value):
        if random.random() < self._fail_rate:
            raise OperationError(f"SET '{key}' failed")
        self._data[key] = value
        return True


# Apply retries to operations
client = UnstableRedis()
random.seed(42)  # For reproducibility


@retry(max_attempts=5, wait=0.05)
def get_client(key):
    return client.get(key)


@retry(max_attempts=5, wait=0.05)
def save_client(key, value):
    return client.set(key, value)


print("=== Retries with RedisConnectionError ===\n")
try:
    result = get_client("user:1")
    print(f"Success: {result}")
except RedisConnectionError as exc:
    print(f"Error after exhausting retries: {exc}")

print("\n=== Retries with OperationError ===\n")
random.seed(100)
try:
    save_client("user:2", {"name": "Bob"})
    print("Saved successfully")
except OperationError as exc:
    print(f"Error after exhausting retries: {exc}")

# Demonstrate that ValidationError is NOT retried
print("\n=== ValidationError is NOT retried ===\n")


@retry(max_attempts=3, wait=0.05)
def validate_and_save(key, value):
    if not key:
        raise ValidationError("Key cannot be empty")
    return client.set(key, value)


try:
    validate_and_save("", "data")
except ValidationError as exc:
    print(f"ValidationError propagated immediately: {exc}")

# Retries with exponential backoff
print("\n=== Exponential backoff ===\n")


def retry_with_backoff(max_attempts=4, retryable_exceptions=None):
    """Decorator with exponential wait between retries."""
    if retryable_exceptions is None:
        retryable_exceptions = (RedisConnectionError, OperationError)

    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as exc:
                    wait_time = 0.05 * (2 ** (attempt - 1))
                    print(f"  Attempt {attempt}/{max_attempts} failed, waiting {wait_time:.2f}s: {exc}")
                    if attempt < max_attempts:
                        time.sleep(wait_time)
            raise exc

        return wrapper

    return decorator


random.seed(200)


@retry_with_backoff(max_attempts=4)
def operation_with_backoff(key):
    if random.random() < 0.6:
        raise RedisConnectionError(f"GET '{key}' failed")
    return "ok"


try:
    result = operation_with_backoff("session:xyz")
    print(f"Success after backoff: {result}")
except RedisConnectionError as exc:
    print(f"Final error: {exc}")
