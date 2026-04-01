"""Async Cache Decorator Example"""

import asyncio
import time
from wredis.decorators import async_cache


@async_cache(ttl=60, prefix="myapp")
async def expensive_async_operation(x, y):
    """This async function only runs if result is not cached."""
    await asyncio.sleep(2)  # Simulate expensive async computation
    return x + y


async def main():
    # First call - will be slow (2 seconds)
    start = time.time()
    result1 = await expensive_async_operation(10, 20)
    print(f"First call: {result1} (took {time.time() - start:.2f}s)")

    # Second call - will be fast (from cache)
    start = time.time()
    result2 = await expensive_async_operation(10, 20)
    print(f"Second call: {result2} (took {time.time() - start:.2f}s)")


if __name__ == "__main__":
    asyncio.run(main())
