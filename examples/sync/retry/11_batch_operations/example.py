"""Example 11: Retry on batch operations.

Demonstrates how to apply @retry to operations that process
multiple elements in batch, retrying the entire batch.
"""

import redis

from wredis._exceptions import OperationError
from wredis._retry import retry


class BatchProcessor:
    """Batch processor with retry support."""

    def __init__(self) -> None:
        self._processed: list[str] = []
        self._attempts = 0

    def process_batch(self, elements: list[str]) -> list[str]:
        """Processes a complete batch of elements."""
        self._attempts += 1
        # Fails on first attempt to demonstrate retry
        if self._attempts <= 1:
            raise redis.ConnectionError("Connection lost during processing")
        self._processed.extend(elements)
        return self._processed


processor = BatchProcessor()


@retry(max_attempts=3, delay=0.1, backoff=2.0)
def execute_batch(elements: list[str]) -> list[str]:
    """Executes a batch of operations with automatic retry."""
    return processor.process_batch(elements)


@retry(max_attempts=3, delay=0.1, backoff=2.0)
def execute_batch_with_permanent_failure(elements: list[str]) -> list[str]:
    """Batch that always fails to demonstrate final error."""
    raise redis.TimeoutError("Batch service permanently offline")


if __name__ == "__main__":
    print("=== Example 11: Batch Operations ===")

    # Batch successful after retry
    batch1 = ["item_1", "item_2", "item_3"]
    result = execute_batch(batch1)
    print(f"Batch 1 processed: {result}")

    # Second batch without failures
    batch2 = ["item_4", "item_5"]
    result2 = execute_batch(batch2)
    print(f"Batch 2 processed: {result2}")

    # Batch with permanent failure
    try:
        execute_batch_with_permanent_failure(["item_x", "item_y"])
    except OperationError as e:
        print(f"Batch with permanent failure: {e}")

    print(f"Total processor attempts: {processor._attempts}")
