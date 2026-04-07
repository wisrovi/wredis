# 12 Async Worker Pattern

Quickly understand if this example fits your needs.

```mermaid
graph LR
    A[Producer] --> B[Work Queue]
    B --> C[Consumer]
    C --> D[Result Queue]
```

## What it does

Implements a producer-consumer pattern using Redis as a message queue, with `AsyncBaseManager` to manage async enqueue and dequeue operations.

## When to use it

- Background job processing
- Task queues
- Message-driven architectures

## Code

```python
# Copy and adapt to your needs
"""12 - Async Worker/Producer pattern

This example implements a producer-consumer pattern using
Redis as a message queue, with AsyncBaseManager to manage
async enqueue and dequeue operations.
"""

import asyncio

import redis.asyncio
from wredis._async_base import AsyncBaseManager

WORK_QUEUE = "queue:jobs"
RESULT_QUEUE = "queue:results"


async def producer(manager: AsyncBaseManager, num_jobs: int):
    """Produces jobs and enqueues them in Redis."""
    for i in range(num_jobs):
        job = f"job_{i}:data_{i * 10}"
        await manager._execute("rpush", WORK_QUEUE, job)
        print(f"  [Producer] Enqueued: {job}")
        await asyncio.sleep(0.05)
    print(f"  [Producer] {num_jobs} jobs produced")


async def consumer(manager: AsyncBaseManager):
    """Consumes jobs from the queue and processes results."""
    processed = 0
    while True:
        job = await manager._execute("lpop", WORK_QUEUE)
        if job is None:
            break

        result = f"result_of_{job}"
        await manager._execute("rpush", RESULT_QUEUE, result)
        print(f"  [Consumer] Processed: {job} -> {result}")
        processed += 1
        await asyncio.sleep(0.02)

    print(f"  [Consumer] {processed} jobs processed")
    return processed


async def main():
    # Create a real Redis client
    client = redis.asyncio.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    async with AsyncBaseManager(verbose=False) as manager:
        manager.redis_client = client

        # Clear previous queues
        await manager._execute("delete", WORK_QUEUE, RESULT_QUEUE)

        print("=== Starting Producer/Consumer pattern ===")

        print("\n--- Production ---")
        await producer(manager, 5)

        print("\n--- Consumption ---")
        total = await consumer(manager)

        # Verify results
        print("\n=== Verification ===")
        length = await manager._execute("llen", RESULT_QUEUE)
        print(f"  Results in queue: {length}")

        results = await manager._execute("lrange", RESULT_QUEUE, 0, -1)
        print(f"  All results: {results}")

    await client.aclose()
    print(f"\nWorker/Consumer pattern completed: {total} jobs processed")


if __name__ == "__main__":
    asyncio.run(main())
```

## Run it

```bash
python example.py
```

## Expected output

```
=== Starting Producer/Consumer pattern ===

--- Production ---
  [Producer] Enqueued: job_0:data_0
  [Producer] Enqueued: job_1:data_10
  [Producer] Enqueued: job_2:data_20
  [Producer] Enqueued: job_3:data_30
  [Producer] Enqueued: job_4:data_40
  [Producer] 5 jobs produced

--- Consumption ---
  [Consumer] Processed: job_0:data_0 -> result_of_job_0:data_0
  [Consumer] Processed: job_1:data_10 -> result_of_job_1:data_10
  [Consumer] Processed: job_2:data_20 -> result_of_job_2:data_20
  [Consumer] Processed: job_3:data_30 -> result_of_job_3:data_30
  [Consumer] Processed: job_4:data_40 -> result_of_job_4:data_40
  [Consumer] 5 jobs processed

=== Verification ===
  Results in queue: 5
  All results: ['result_of_job_0:data_0', 'result_of_job_1:data_10', ...]

Worker/Consumer pattern completed: 5 jobs processed
```