"""Example 06: Retry on Redis database connections.

Shows how to use @retry to establish connections to Redis in a
resilient way against temporary network failures.
"""

import redis

from wredis._exceptions import OperationError
from wredis._retry import retry


class ConnectionManager:
    """Redis connection manager with integrated retry."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self._connection: redis.Redis | None = None
        self._connection_attempts = 0

    @retry(max_attempts=4, delay=0.1, backoff=2.0)
    def connect(self) -> redis.Redis:
        """Establishes connection to Redis with automatic retries."""
        self._connection_attempts += 1
        if self._connection_attempts < 3:
            raise redis.ConnectionError(f"Could not connect to {self.host}:{self.port}")
        # Simulating successful connection
        self._connection = redis.Redis(host=self.host, port=self.port)
        return self._connection

    @retry(max_attempts=3, delay=0.05, backoff=1.5)
    def verify_connection(self) -> bool:
        """Verifies that the connection is active with ping."""
        if self._connection_attempts < 3:
            raise redis.ConnectionError("Unstable connection")
        return True


if __name__ == "__main__":
    print("=== Example 06: Database Connection ===")

    manager = ConnectionManager("localhost", 6379)

    # Connect with retries
    connection = manager.connect()
    print(f"Connection established: {connection}")

    # Verify connection
    active = manager.verify_connection()
    print(f"Connection active: {active}")
    print(f"Total connection attempts: {manager._connection_attempts}")
