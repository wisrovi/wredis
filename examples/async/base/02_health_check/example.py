"""02 - Health check

This example demonstrates the use of the health_check() method to
verify that the Redis connection is active and working correctly,
including error handling.
"""

import asyncio

from wredis._exceptions import OperationError
from wredis.aio import BaseManager


async def main():
    manager = BaseManager(verbose=True)

    try:
        status = await manager.health_check()
        print(f"Connection status: {status}")
    except OperationError as e:
        print(f"Health check error: {e}")

    if await manager.health_check():
        print("Connection verified, proceeding with operations")
        await manager._execute("set", "status", "operational")
        value = await manager._execute("get", "status")
        print(f"Stored value: {value}")
    else:
        print("Connection not available")

    await manager.close()
    print("Connection closed")


if __name__ == "__main__":
    asyncio.run(main())
