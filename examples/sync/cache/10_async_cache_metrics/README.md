# 10 Async Cache Metrics

Quickly understand if this example fits your needs.

```mermaid
graph LR
    A[Async Call] --> B[@async_cache]
    B --> C{Cache Hit?}
    C -->|Yes| D[Return Cached]
    C -->|No| E[Execute Async]
    E --> F[Store in Redis]
    F --> D
```

## What it does

Demonstrates using CacheMetrics with async functions via the @async_cache decorator.

## When to use it

- When caching async functions
- When working with async frameworks
- When measuring async operation performance

## Code

```python
# Copy and adapt to your needs
import asyncio
import redis
import redis.asyncio as aredis
from wredis.decorators import async_cache, CacheMetrics


async def main():
    redis_client = aredis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    metrics = CacheMetrics()

    @async_cache(ttl=300, prefix="async_data", redis_client=redis_client, metrics=metrics)
    async def obtener_datos_async(item_id: int) -> dict:
        """Simulates expensive async operation."""
        await asyncio.sleep(0.01)
        return {"id": item_id, "datos": f"datos_async_{item_id}"}

    # First call: miss
    print("=== First call (miss) ===")
    resultado = await obtener_datos_async(1)
    print(f"Result: {resultado}")
    print(f"Metrics: hits={metrics.hits}, misses={metrics.misses}")

    # Second call: hit
    print("\n=== Second call (hit) ===")
    resultado = await obtener_datos_async(1)
    print(f"Result: {resultado}")
    print(f"Metrics: hits={metrics.hits}, misses={metrics.misses}")

    # Multiple calls
    print("\n=== Multiple calls ===")
    for i in [2, 1, 3, 1, 2]:
        await obtener_datos_async(i)

    print(f"\n=== Final Summary ===")
    print(f"Metrics: {metrics}")
    print(f"Hit rate: {metrics.hit_rate:.1f}%")

    await redis_client.close()


asyncio.run(main())
```

## Run it

```bash
python example.py
```

## Expected output

Shows metrics tracking for async operations with hits on repeated calls.
