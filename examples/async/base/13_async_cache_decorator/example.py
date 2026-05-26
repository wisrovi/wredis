"""13 - Async cache decorator

This example implements a custom decorator that uses
BaseManager to cache results of async functions,
avoiding redundant executions with configurable TTL.
"""

import asyncio
import functools
from typing import Any, Callable

from wredis.aio import BaseManager

_cache_manager: BaseManager | None = None


def cache(ttl: int = 300, prefix: str = "cache"):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            global _cache_manager
            if _cache_manager is None:
                raise RuntimeError("Cache manager not initialized")

            key_args = "_".join(str(a) for a in args)
            key_kwargs = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = f"{prefix}:{func.__name__}:{key_args}:{key_kwargs}"

            cached_result = await _cache_manager._execute("get", cache_key)
            if cached_result is not None:
                print(f"  [CACHE HIT] {cache_key}")
                return cached_result

            print(f"  [CACHE MISS] {cache_key} - executing function")
            result = await func(*args, **kwargs)

            await _cache_manager._execute("set", cache_key, str(result), ex=ttl)
            return result

        return wrapper

    return decorator


@cache(ttl=60, prefix="app")
async def calculate_statistics(report_id: int):
    await asyncio.sleep(0.1)
    return f"statistics_of_report_{report_id}"


async def main():
    global _cache_manager

    async with BaseManager(verbose=False) as manager:
        _cache_manager = manager

        print("=== First call (CACHE MISS) ===")
        result1 = await calculate_statistics(42)
        print(f"  Result: {result1}")

        print("\n=== Second identical call (CACHE HIT) ===")
        result2 = await calculate_statistics(42)
        print(f"  Result: {result2}")

        print("\n=== Third call with different args (CACHE MISS) ===")
        result3 = await calculate_statistics(99)
        print(f"  Result: {result3}")

        print("\n=== Fourth call same as first (CACHE HIT) ===")
        result4 = await calculate_statistics(42)
        print(f"  Result: {result4}")

        print("\n=== Keys in cache ===")
        keys = await manager._execute("keys", "app:*")
        for key in sorted(keys):
            value = await manager._execute("get", key)
            ttl = await manager._execute("ttl", key)
            print(f"  {key} = {value} (TTL: {ttl}s)")

    _cache_manager = None
    print("\nCache decorator completed")


if __name__ == "__main__":
    asyncio.run(main())
