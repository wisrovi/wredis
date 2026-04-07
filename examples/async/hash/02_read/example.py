"""Async Hash Example - Read"""

import asyncio

from wredis.aio import RedisHashManager


async def main():
    manager = RedisHashManager(host="localhost")
    user1 = await manager.read_hash("my_hash", "user:1")
    all_users = await manager.read_all_hash("my_hash")

    print(f"User 1: {user1}")
    print(f"All users: {all_users}")


if __name__ == "__main__":
    asyncio.run(main())
