"""07 - Connection pool configuration

This example shows how to configure the Redis connection pool
with custom parameters like max_connections, socket_timeout
and decode_responses to optimize performance.
"""

import asyncio

from wredis.aio import BaseManager


async def main():
    manager = BaseManager(
        decode_responses=True,
        socket_timeout=10.0,
        max_connections=20,
        verbose=True,
    )

    connected = await manager.health_check()
    print(f"Connection established: {connected}")

    for i in range(5):
        await manager._execute("set", f"pool:key:{i}", f"value_{i}")
        print(f"  Set pool:key:{i} -> value_{i}")

    print("\nReading keys from pool:")
    for i in range(5):
        value = await manager._execute("get", f"pool:key:{i}")
        print(f"  pool:key:{i} = {value}")

    print("\nMaximum pool size: 20 connections")
    print("Socket timeout: 10.0 seconds")
    print("Decode responses: True")

    await manager.close()
    print("\nConnection pool closed")


if __name__ == "__main__":
    asyncio.run(main())
