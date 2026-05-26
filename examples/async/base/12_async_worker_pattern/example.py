"""12 - Async Worker/Producer pattern

This example implements a producer-consumer pattern using
Redis as a message queue, with BaseManager to manage
async enqueue and dequeue operations.
"""

import asyncio

from wredis.aio import BaseManager

WORK_QUEUE = "queue:jobs"
RESULT_QUEUE = "queue:results"


async def producer(manager: BaseManager, num_jobs: int):
    for i in range(num_jobs):
        job = f"job_{i}:data_{i * 10}"
        await manager._execute("rpush", WORK_QUEUE, job)
        print(f"  [Producer] Enqueued: {job}")
        await asyncio.sleep(0.05)
    print(f"  [Producer] {num_jobs} jobs produced")


async def consumer(manager: BaseManager):
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
    async with BaseManager(verbose=False) as manager:
        await manager._execute("delete", WORK_QUEUE, RESULT_QUEUE)

        print("=== Starting Producer/Consumer pattern ===")

        print("\n--- Production ---")
        await producer(manager, 5)

        print("\n--- Consumption ---")
        total = await consumer(manager)

        print("\n=== Verification ===")
        length = await manager._execute("llen", RESULT_QUEUE)
        print(f"  Results in queue: {length}")

        results = await manager._execute("lrange", RESULT_QUEUE, 0, -1)
        print(f"  All results: {results}")

    print(f"\nWorker/Consumer pattern completed: {total} jobs processed")


if __name__ == "__main__":
    asyncio.run(main())
