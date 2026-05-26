"""Example 08: Circuit breaker pattern with retry.

Implements a simple circuit breaker that stops retrying when
too many consecutive failures are detected.
"""

import redis

from wredis._exceptions import OperationError
from wredis._retry import retry


class CircuitBreaker:
    """Simple circuit breaker to protect against repeated failures."""

    def __init__(self, max_failures: int = 5) -> None:
        self.max_failures = max_failures
        self.consecutive_failures = 0
        self.open = False

    def register_success(self) -> None:
        """Registers a successful operation and resets the counter."""
        self.consecutive_failures = 0
        self.open = False

    def register_failure(self) -> None:
        """Registers a failure and opens the circuit if limit is exceeded."""
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.max_failures:
            self.open = True
            print(
                f"  [CIRCUIT BREAKER] Circuit OPEN after {self.consecutive_failures} failures"
            )

    def verify(self) -> None:
        """Verifies if circuit is open before executing."""
        if self.open:
            raise OperationError("Circuit breaker open: service unavailable")


# Global circuit breaker instance
cb = CircuitBreaker(max_failures=3)
call_count = 0


@retry(max_attempts=3, delay=0.05, backoff=1.0)
def protected_operation() -> str:
    """Operation protected by circuit breaker."""
    cb.verify()

    global call_count
    call_count += 1

    # Simulate permanent failure
    raise redis.ConnectionError("Service not responding")


if __name__ == "__main__":
    print("=== Example 08: Circuit Breaker ===")

    # First call: fails, retry attempts
    try:
        protected_operation()
    except OperationError as e:
        print(f"Error after retries: {e}")
        cb.register_failure()

    # Second call: circuit breaker still allows
    try:
        protected_operation()
    except OperationError as e:
        print(f"Error after retries: {e}")
        cb.register_failure()

    # Third call: opens the circuit breaker
    try:
        protected_operation()
    except OperationError as e:
        print(f"Error after retries: {e}")
        cb.register_failure()

    # Fourth call: circuit breaker blocks immediately
    print(f"\nCircuit breaker state: {'OPEN' if cb.open else 'CLOSED'}")
    print(f"Consecutive failures: {cb.consecutive_failures}")
    print(f"Total calls executed: {call_count}")
