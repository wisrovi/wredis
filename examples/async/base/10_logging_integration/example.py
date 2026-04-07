"""10 - Integrated logging system

This example shows the use of the log() method from BaseManager
to log messages with different severity levels integrated with loguru.
"""

import asyncio

from wredis.aio import BaseManager


async def main():
    async with BaseManager(verbose=True) as manager:
        connected = await manager.health_check()
        print(f"Connection established: {connected}")

        print("\n=== Log messages ===")
        manager.log("Application started successfully", "info")
        manager.log("Processing user data", "debug")
        manager.log("Warning: cache almost full", "warning")

        print("\n=== Operations with logging ===")
        await manager._execute("set", "app:status", "running")
        manager.log("Application status updated", "info")

        status = await manager._execute("get", "app:status")
        print(f"Current status: {status}")

        manager.log("Attempting critical operation...", "info")
        try:
            await manager._execute("set", "app:data", '{"items": [1, 2, 3]}')
            manager.log("Critical data saved successfully", "info")
        except Exception as e:
            manager.log(f"Error saving data: {e}", "error")

        manager.log("Process completed without errors", "info")

    print("\nLogging system completed")


if __name__ == "__main__":
    asyncio.run(main())
