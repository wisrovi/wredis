"""Basic cache metrics tracking.

This example demonstrates how to use CacheMetrics to track
cache hits and misses in simple operations with @cache.
"""

from wredis.decorators import CacheMetrics, cache
from wredis.sync import BaseManager

manager = BaseManager(verbose=False)

metrics = CacheMetrics()


@cache(ttl=300, prefix="usuario", redis_client=manager.redis_client, metrics=metrics)
def obtener_usuario(user_id: int) -> dict:
    """Simulates an expensive database query."""
    return {"id": user_id, "nombre": f"Usuario_{user_id}"}


print("=== First call (miss) ===")
resultado = obtener_usuario(1)
print(f"Result: {resultado}")
print(f"Metrics: hits={metrics.hits}, misses={metrics.misses}")
print()

print("=== Second call (hit) ===")
resultado = obtener_usuario(1)
print(f"Result: {resultado}")
print(f"Metrics: hits={metrics.hits}, misses={metrics.misses}")
print()

print("=== Third call with different ID (miss) ===")
resultado = obtener_usuario(2)
print(f"Result: {resultado}")
print(f"Metrics: hits={metrics.hits}, misses={metrics.misses}")
print()

print("=== Summary ===")
print(f"Final metrics: {metrics}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")

manager.close()
