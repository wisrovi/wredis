"""Async Bitmap Example - Write"""

import asyncio

from wredis.aio import RedisBitmapManager


async def main():
    manager = RedisBitmapManager(host="localhost")
    await manager.set_bit(key="my_bitmap", offset=5, value=1)
    await manager.set_bit(key="my_bitmap", offset=10, value=1, ttl=300)

    print("Bitmap operations completed")


if __name__ == "__main__":
    asyncio.run(main())
