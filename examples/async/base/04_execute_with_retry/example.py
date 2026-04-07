"""04 - Execution with retry (_execute)

This example demonstrates the _execute() method that runs Redis
operations with exponential retry logic (up to 3 attempts) on
connection failures.
"""

import asyncio

from wredis.aio import BaseManager


async def main():
    async with BaseManager(verbose=True) as manager:
        result_set = await manager._execute("set", "user:1:name", "Ana")
        print(f"SET user:1:name = {result_set}")

        name = await manager._execute("get", "user:1:name")
        print(f"GET user:1:name = {name}")

        await manager._execute("set", "token:abc123", "secret", ex=300)
        ttl = await manager._execute("ttl", "token:abc123")
        print(f"Token TTL: {ttl} seconds")

        exists = await manager._execute("exists", "user:1:name")
        print(f"Does user:1:name exist? {bool(exists)}")

        deleted = await manager._execute("delete", "user:1:name")
        print(f"Keys deleted: {deleted}")

    print("Operations with retry completed")


if __name__ == "__main__":
    asyncio.run(main())
