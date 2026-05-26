"""Example 14: Async retry decorator.

Shows the use of async_retry for async/await functions with
automatic retry using asyncio.sleep.
"""

import asyncio

import redis

from wredis._exceptions import OperationError
from wredis._retry import async_retry


class MockAsyncService:
    """Mock async service for demonstration."""

    def __init__(self) -> None:
        self._attempts = 0

    async def query(self, resource: str) -> dict:
        """Simulates async query with intermittent failures."""
        self._attempts += 1
        await asyncio.sleep(0.01)  # Simulates network latency
        if self._attempts <= 2:
            raise redis.TimeoutError("Timeout in async query")
        return {"resource": resource, "data": "information obtained"}


service = MockAsyncService()


@async_retry(max_attempts=4, delay=0.1, backoff=2.0)
async def get_resource(resource: str) -> dict:
    """Gets a resource with async retry."""
    return await service.query(resource)


@async_retry(max_attempts=3, delay=0.05, backoff=1.5)
async def operation_that_fails() -> str:
    """Async operation that always fails."""
    raise redis.ConnectionError("Async connection lost")


async def main() -> None:
    """Main async function."""
    print("=== Example 14: Async Retry ===")

    # Operation successful after retries
    result = await get_resource("users")
    print(f"Result: {result}")
    print(f"Attempts made: {service._attempts}")

    # Operation that fails permanently
    try:
        await operation_that_fails()
    except OperationError as e:
        print(f"Async error after retries: {e}")


if __name__ == "__main__":
    asyncio.run(main())
