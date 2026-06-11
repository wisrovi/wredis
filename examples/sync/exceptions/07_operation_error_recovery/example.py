"""OperationError recovery demonstration.

Shows how to detect OperationError and apply recovery strategies
such as retries or alternative operations.
"""

import time

from wredis._exceptions import OperationError


class SimulatedRedis:
    """Simulates a Redis client that may temporarily fail."""

    def __init__(self):
        self._data = {}
        self._fail = True
        self._attempts = 0

    def simulate_recovery(self):
        """Makes operations start succeeding."""
        self._fail = False

    def get(self, key):
        """Simulates a GET that may fail."""
        self._attempts += 1
        if self._fail:
            raise OperationError(f"GET '{key}' failed (attempt {self._attempts})")
        return self._data.get(key)

    def set(self, key, value):
        """Simulates a SET that may fail."""
        self._attempts += 1
        if self._fail:
            raise OperationError(f"SET '{key}' failed (attempt {self._attempts})")
        self._data[key] = value
        return True


def operation_with_retry(client, operation, max_attempts=3):
    """Executes an operation with retries on OperationError.

    Args:
        client: SimulatedRedis instance.
        operation: Function that executes the operation.
        max_attempts: Maximum number of retries.

    Returns:
        The result of the operation.

    Raises:
        OperationError: If retries are exhausted.
    """
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationError as exc:
            last_error = exc
            print(f"  Attempt {attempt}/{max_attempts} failed: {exc}")
            if attempt < max_attempts:
                time.sleep(0.1)  # Brief wait before retry
    raise last_error


# Scenario 1: Operation that fails permanently
print("=== Scenario 1: Permanent failure ===")
client = SimulatedRedis()
try:
    result = operation_with_retry(client, lambda: client.get("user:1"), max_attempts=3)
    print(f"Result: {result}")
except OperationError as exc:
    print(f"Final error after exhausting retries: {exc}")

# Scenario 2: Operation that recovers
print("\n=== Scenario 2: Recovery after retries ===")
client2 = SimulatedRedis()


def get_with_recovery():
    client2._attempts += 0  # Already counts internally
    if client2._attempts >= 2:
        client2.simulate_recovery()
    return client2.get("user:1")


try:
    result = operation_with_retry(client2, get_with_recovery, max_attempts=5)
    print(f"Result after recovery: {result}")
except OperationError as exc:
    print(f"Final error: {exc}")

# Scenario 3: Fallback to default value
print("\n=== Scenario 3: Fallback to default value ===")
client3 = SimulatedRedis()
try:
    result = client3.get("config:theme")
except OperationError:
    result = "light_theme"  # Default value
    print(f"Using default value: {result}")
