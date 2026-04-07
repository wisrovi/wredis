"""06 - Concurrent operations

This example demonstrates how to execute multiple Redis operations
concurrently using asyncio.gather() to maximize performance on
independent operations.
"""

import asyncio

from wredis.aio import BaseManager


async def write_data(manager: BaseManager, key: str, value: str):
    await manager._execute("set", key, value)
    return f"Written: {key}={value}"


async def read_data(manager: BaseManager, key: str):
    value = await manager._execute("get", key)
    return f"Read: {key}={value}"


async def main():
    async with BaseManager(verbose=False) as manager:
        print("=== Concurrent Write ===")
        write_tasks = [
            write_data(manager, f"user:{i}", f"name_{i}") for i in range(1, 6)
        ]
        results = await asyncio.gather(*write_tasks)
        for r in results:
            print(f"  {r}")

        print("\n=== Concurrent Read ===")
        read_tasks = [read_data(manager, f"user:{i}") for i in range(1, 6)]
        results = await asyncio.gather(*read_tasks)
        for r in results:
            print(f"  {r}")

        print("\n=== Concurrent Mixed Operations ===")
        mixed = [
            manager._execute("set", "temp", "data"),
            manager._execute("get", "user:1"),
            manager._execute("exists", "user:3"),
            manager._execute("ttl", "user:5"),
        ]
        mixed_results = await asyncio.gather(*mixed)
        print(f"  SET temp: {mixed_results[0]}")
        print(f"  GET user:1: {mixed_results[1]}")
        print(f"  EXISTS user:3: {bool(mixed_results[2])}")
        print(f"  TTL user:5: {mixed_results[3]}")

    print("\nConcurrent operations completed")


if __name__ == "__main__":
    asyncio.run(main())
