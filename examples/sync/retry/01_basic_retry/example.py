"""Example 01: Basic retry decorator usage.

Demonstrates how the @retry decorator automatically retries a function
that fails with redis.ConnectionError until exhausting configured attempts.
"""

import redis

from wredis._retry import retry

# Simulated function that fails the first 2 times
attempts = 0


@retry(max_attempts=3, delay=0.1, backoff=1.0)
def unstable_operation() -> str:
    """Simulates an operation that fails intermittently."""
    global attempts
    attempts += 1
    if attempts < 3:
        raise redis.ConnectionError("Intermittent connection lost")
    return "Operation successful on attempt 3"


if __name__ == "__main__":
    print("=== Example 01: Basic Retry ===")
    result = unstable_operation()
    print(f"Result: {result}")
    print(f"Total attempts made: {attempts}")
