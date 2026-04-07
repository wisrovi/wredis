"""Hit rate monitoring.

This example shows how to calculate and monitor the cache hit rate
using the hit_rate property of CacheMetrics.
"""

from wredis.decorators import CacheMetrics, cache
from wredis.sync import BaseManager

manager = BaseManager(verbose=False)
metrics = CacheMetrics()


@cache(ttl=600, prefix="producto", redis_client=manager.redis_client, metrics=metrics)
def obtener_producto(producto_id: int) -> dict:
    """Simulates a product catalog query."""
    return {
        "id": producto_id,
        "nombre": f"Producto_{producto_id}",
        "precio": producto_id * 10.5,
    }


patron_acceso = [1, 2, 1, 3, 1, 2, 4, 1, 5, 1]

for i, pid in enumerate(patron_acceso, 1):
    resultado = obtener_producto(pid)
    print(f"Access #{i}: producto_id={pid} -> {resultado['nombre']}")
    print(f"  Current hit rate: {metrics.hit_rate:.1f}%")

print()
print("=== Final Summary ===")
print(f"Total hits: {metrics.hits}")
print(f"Total misses: {metrics.misses}")
print(f"Total errors: {metrics.errors}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")
print(f"Representation: {metrics}")

manager.close()
