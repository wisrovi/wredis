"""Example 13: Retry with maximum timeout.

Demonstrates how to limit the total retry time to prevent
an operation from blocking indefinitely.
"""

import time

import redis

from wredis._exceptions import OperationError
from wredis._retry import retry


class OperationWithTimeout:
    """Operation that respects a maximum timeout."""

    def __init__(self, total_timeout: float) -> None:
        self.total_timeout = total_timeout
        self._start: float = 0
        self._attempts = 0

    def check_timeout(self) -> None:
        """Checks if total timeout was exceeded."""
        elapsed = time.time() - self._start
        if elapsed > self.total_timeout:
            raise TimeoutError(
                f"Timeout of {self.total_timeout}s exceeded (elapsed: {elapsed:.2f}s)"
            )

    @retry(max_attempts=10, delay=0.2, backoff=1.5)
    def execute(self) -> str:
        """Executes operation with timeout verification."""
        self._attempts += 1
        self.check_timeout()
        raise redis.ConnectionError("Service not responding")


if __name__ == "__main__":
    print("=== Example 13: Retry with Timeout ===")

    # Short timeout: stops before exhausting all attempts
    short_op = OperationWithTimeout(total_timeout=0.5)
    short_op._start = time.time()

    try:
        short_op.execute()
    except TimeoutError as e:
        print(f"Timeout detected: {e}")
    except OperationError as e:
        print(f"Operation error: {e}")

    print(f"Attempts made before timeout: {short_op._attempts}")

    # Long timeout: allows more retries
    print("\n--- With longer timeout ---")
    long_op = OperationWithTimeout(total_timeout=2.0)
    long_op._start = time.time()

    try:
        long_op.execute()
    except TimeoutError as e:
        print(f"Timeout detected: {e}")
    except OperationError as e:
        print(f"Operation error (exhausted attempts): {e}")

    print(f"Attempts made: {long_op._attempts}")
