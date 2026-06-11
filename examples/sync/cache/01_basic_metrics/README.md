# 01 Basic Metrics

Quickly understand if this example fits your needs.

```mermaid
graph LR
    A[Function Call] --> B[@cache Decorator]
    B --> C{Cache Hit?}
    C -->|Yes| D[Return Cached]
    C -->|No| E[Execute Function]
    E --> F[Store in Redis]
    F --> D
```

## What it does

Demonstrates basic cache metrics tracking using CacheMetrics to monitor hits and misses with the @cache decorator.

## When to use it

- When you need to monitor basic cache performance
- When starting to integrate caching in your application
- When you want to understand cache hit/miss patterns

## Code

```python
# Copy and adapt to your needs
import redis
from wredis.decorators import cache, CacheMetrics

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

metrics = CacheMetrics()


@cache(ttl=300, prefix="usuario", redis_client=redis_client, metrics=metrics)
def obtener_usuario(user_id: int) -> dict:
    """Simulates an expensive database query."""
    return {"id": user_id, "nombre": f"Usuario_{user_id}"}


# First call: cache miss
print("=== First call (miss) ===")
resultado = obtener_usuario(1)
print(f"Result: {resultado}")
print(f"Metrics: hits={metrics.hits}, misses={metrics.misses}")

# Second call: cache hit
print("=== Second call (hit) ===")
resultado = obtener_usuario(1)
print(f"Result: {resultado}")
print(f"Metrics: hits={metrics.hits}, misses={metrics.misses}")

# Third call with different argument: another miss
print("=== Third call with different ID (miss) ===")
resultado = obtener_usuario(2)
print(f"Result: {resultado}")
print(f"Metrics: hits={metrics.hits}, misses={metrics.misses}")

# Final summary
print(f"=== Summary ===")
print(f"Final metrics: {metrics}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")

redis_client.close()
```

## Run it

```bash
python example.py
```

## Expected output

Shows cache misses on first calls and hits on subsequent calls with the same arguments, with final hit rate calculation.
