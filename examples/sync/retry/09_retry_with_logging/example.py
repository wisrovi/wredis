"""Example 09: Retry with logging and monitoring.

Demonstrates how to add logging to operations with retry to
monitor retries and diagnose problems.
"""

import redis

from wredis._exceptions import OperationError
from wredis._retry import retry


class RetryMonitor:
    """Monitor that records retry statistics."""

    def __init__(self) -> None:
        self.total_operations = 0
        self.total_retries = 0
        self.successful_operations = 0
        self.failed_operations = 0

    def register_operation(self, name: str, success: bool, retries: int) -> None:
        """Registers the result of an operation."""
        self.total_operations += 1
        self.total_retries += retries
        if success:
            self.successful_operations += 1
        else:
            self.failed_operations += 1
        print(f"  [LOG] {name}: {'SUCCESS' if success else 'FAILURE'} (retries: {retries})")

    def summary(self) -> dict:
        """Returns accumulated statistics."""
        return {
            "total_operations": self.total_operations,
            "total_retries": self.total_retries,
            "successful": self.successful_operations,
            "failed": self.failed_operations,
        }


monitor = RetryMonitor()
simulated_failures = {"op_a": 1, "op_b": 0, "op_c": 5}  # op_c never succeeds


def create_operation(name: str):
    """Factory to create operations with monitoring."""
    attempts = [0]

    @retry(max_attempts=4, delay=0.05, backoff=1.0)
    def operation() -> str:
        attempts[0] += 1
        if attempts[0] <= simulated_failures.get(name, 0):
            raise redis.ConnectionError(f"Simulated failure in {name}")
        return f"Result of {name}"

    return operation, attempts


if __name__ == "__main__":
    print("=== Example 09: Logging and Monitoring ===")

    operations = {
        "op_a": create_operation("op_a"),  # Fails 1 time, then success
        "op_b": create_operation("op_b"),  # No failures
        "op_c": create_operation("op_c"),  # Always fails
    }

    for name, (func, attempts_ref) in operations.items():
        try:
            result = func()
            monitor.register_operation(name, True, attempts_ref[0] - 1)
            print(f"  Result: {result}")
        except OperationError:
            monitor.register_operation(name, False, attempts_ref[0])

    print("\nMonitor summary:")
    for key, value in monitor.summary().items():
        print(f"  {key}: {value}")
