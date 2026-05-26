"""Async Bitmap Example - Read"""

import asyncio

from wredis.aio import RedisBitmapManager


async def main():
    manager = RedisBitmapManager(host="localhost")

    bit_value = await manager.get_bit("my_bitmap", 0)
    bit_count = await manager.count_bits("my_bitmap")
    ttl = await manager.get_ttl("my_bitmap")

    print(f"Bit value: {bit_value}")
    print(f"Bit count: {bit_count}")
    print(f"TTL: {ttl}")


if __name__ == "__main__":
    asyncio.run(main())
