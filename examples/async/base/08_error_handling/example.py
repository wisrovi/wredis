"""08 - Error handling

This example demonstrates error handling strategies when using
BaseManager, including catching OperationError, automatic
retries and graceful degradation.
"""

import asyncio

from wredis._exceptions import OperationError
from wredis.aio import BaseManager


async def main():
    async with BaseManager(verbose=True) as manager:
        print("=== 1. Health check with try/except ===")
        try:
            status = await manager.health_check()
            print(f"  Health check successful: {status}")
        except OperationError as e:
            print(f"  Connection error: {e}")

        print("\n=== 2. Operation with try/except ===")
        try:
            await manager._execute("set", "secure:data", "valid_value")
            result = await manager._execute("get", "secure:data")
            print(f"  Operation successful: {result}")
        except OperationError as e:
            print(f"  Operation error: {e}")

        print("\n=== 3. Operation with invalid arguments ===")
        try:
            await manager._execute("get", "key1", "key2")
        except (OperationError, Exception) as e:
            print(f"  Error caught: {type(e).__name__}: {e}")

        print("\n=== 4. Graceful degradation ===")
        cache_key = "config:app"
        try:
            cached_value = await manager._execute("get", cache_key)
            if cached_value:
                config = cached_value
            else:
                config = "default_configuration"
                await manager._execute("set", cache_key, config, ex=60)
            print(f"  Configuration obtained: {config}")
        except OperationError:
            config = "fallback_configuration"
            print(f"  Using fallback: {config}")

        print("\n=== 5. Automatic retry ===")
        print("  _execute automatically retries up to 3 times")
        print("  with exponential backoff: 0.1s, 0.2s")
        await manager._execute("set", "retry:key", "safe_value")
        print(f"  Operation completed with retries enabled")

    print("\nError handling completed")


if __name__ == "__main__":
    asyncio.run(main())
