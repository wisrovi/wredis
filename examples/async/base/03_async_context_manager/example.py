"""03 - Async context manager usage

This example shows how to use BaseManager as an async context
manager with 'async with', which guarantees that the connection is
automatically closed when exiting the block.
"""

import asyncio

from wredis.aio import BaseManager


async def main():
    async with BaseManager(verbose=True) as manager:
        connected = await manager.health_check()
        print(f"Inside context - Connected: {connected}")

        await manager._execute("set", "key1", "value1")
        await manager._execute("set", "key2", "value2")

        value1 = await manager._execute("get", "key1")
        value2 = await manager._execute("get", "key2")
        print(f"key1 = {value1}, key2 = {value2}")

    print("Outside context - connection closed automatically")


if __name__ == "__main__":
    asyncio.run(main())
