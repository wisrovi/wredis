"""Async Hash Example - Write"""

import asyncio

from wredis.aio import RedisHashManager


async def main():
    manager = RedisHashManager(host="localhost")

    await manager.create_hash("my_hash", "user:1", {"name": "Alice", "age": 30}, ttl=60)
    await manager.create_hash("my_hash", "user:2", {"name": "Bob", "age": 25})

    print("Hash created")


if __name__ == "__main__":
    asyncio.run(main())
