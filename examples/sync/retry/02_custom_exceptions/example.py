"""Example 02: Retry with custom exceptions.

Shows how to configure the @retry decorator to catch exception types
other than the default Redis exceptions.
"""

import redis

from wredis._exceptions import OperationError
from wredis._retry import retry


# Custom exception to simulate a business error
class ServiceUnavailableError(Exception):
    """Error when an external service is unavailable."""


# Exception for corrupted data
class CorruptedDataError(Exception):
    """Error when received data is corrupted."""


counter = 0


@retry(
    max_attempts=4,
    delay=0.05,
    backoff=1.0,
    exceptions=(ServiceUnavailableError, redis.TimeoutError),
)
def query_service() -> str:
    """Queries a service that may fail due to unavailability."""
    global counter
    counter += 1
    if counter <= 2:
        raise ServiceUnavailableError("Service temporarily offline")
    return "Data obtained correctly"


if __name__ == "__main__":
    print("=== Example 02: Custom Exceptions ===")

    # This function succeeds after 2 retries
    result = query_service()
    print(f"Result: {result}")
    print(f"Attempts made: {counter}")

    # This function always fails with an exception NOT configured
    @retry(max_attempts=2, delay=0.05, backoff=1.0, exceptions=(redis.ConnectionError,))
    def operation_with_corrupted_data() -> str:
        """Operation that fails with exception not caught by retry."""
        raise CorruptedDataError("Data is corrupted")

    try:
        operation_with_corrupted_data()
    except CorruptedDataError as e:
        print(f"Exception not caught by retry (as expected): {e}")
