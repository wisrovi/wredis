"""Metrics with async functions using @cache.

This example shows how to use CacheMetrics with the
cache decorator for async functions.
"""

import asyncio

import redis.asyncio as aredis

from wredis.aio import CacheMetrics, cache


async def main():
    redis_client = aredis.Redis(
        host="localhost", port=6379, db=0, decode_responses=True
    )
    metrics = CacheMetrics()

    @cache(ttl=300, prefix="async_data", redis_client=redis_client, metrics=metrics)
    async def obtener_datos_async(item_id: int) -> dict:
        """Simulates expensive async operation."""
        await asyncio.sleep(0.01)  # Simulate network latency
        return {"id": item_id, "datos": f"datos_async_{item_id}"}

    print("=== First call (miss) ===")
    resultado = await obtener_datos_async(1)
    print(f"Result: {resultado}")
    print(f"Metrics: hits={metrics.hits}, misses={metrics.misses}")

    print("\n=== Second call (hit) ===")
    resultado = await obtener_datos_async(1)
    print(f"Result: {resultado}")
    print(f"Metrics: hits={metrics.hits}, misses={metrics.misses}")

    print("\n=== Multiple calls ===")
    for i in [2, 1, 3, 1, 2]:
        await obtener_datos_async(i)

    print(f"\n=== Final Summary ===")
    print(f"Metrics: {metrics}")
    print(f"Hit rate: {metrics.hit_rate:.1f}%")

    await redis_client.close()


asyncio.run(main())
