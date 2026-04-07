"""Example 03: Exponential backoff timing.

Demonstrates how the backoff parameter multiplies the delay between
each retry, creating increasingly longer pauses.
"""

import time

import redis

from wredis._retry import retry

# Timestamp记录 to measure delays
timestamps: list[float] = []


@retry(max_attempts=5, delay=0.1, backoff=2.0)
def operation_with_backoff() -> str:
    """Operation that always fails to demonstrate backoff."""
    timestamps.append(time.time())
    raise redis.ConnectionError("Connection refused")


if __name__ == "__main__":
    print("=== Example 03: Exponential Backoff ===")

    try:
        operation_with_backoff()
    except Exception as e:
        print(f"Final error: {e}")

    # Calculate actual delays between attempts
    print("\nTimes between attempts:")
    for i in range(1, len(timestamps)):
        actual_delay = timestamps[i] - timestamps[i - 1]
        expected_delay = 0.1 * (2.0 ** (i - 1))
        print(
            f"  Attempt {i} -> {i + 1}: actual_delay={actual_delay:.3f}s, expected_delay={expected_delay:.3f}s"
        )

    print(f"\nTotal attempts: {len(timestamps)}")
