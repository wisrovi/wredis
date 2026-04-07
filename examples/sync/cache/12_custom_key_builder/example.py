"""Custom prefixes and key builders with metrics.

This example shows how to use custom prefixes and custom
functions to build cache keys along with metrics.
"""

from wredis.decorators import CacheMetrics, cache
from wredis.sync import BaseManager

manager = BaseManager(verbose=False)
metrics = CacheMetrics()


def mi_key_builder(func, args, kwargs) -> str:
    """Custom cache key builder."""
    return f"custom:{func.__name__}:{args[0]}"


@cache(
    ttl=300,
    prefix="app",
    key_builder=mi_key_builder,
    redis_client=manager.redis_client,
    metrics=metrics,
)
def buscar_usuario(username: str) -> dict:
    """Searches user by username."""
    return {"username": username, "email": f"{username}@ejemplo.com"}


@cache(
    ttl=300,
    prefix="app",
    key_builder=mi_key_builder,
    redis_client=manager.redis_client,
    metrics=metrics,
)
def buscar_producto(sku: str) -> dict:
    """Searches product by SKU."""
    return {"sku": sku, "nombre": f"Producto_{sku}"}


print("=== Searches with custom key builder ===")

print("\n--- Search users ---")
buscar_usuario("juan")
buscar_usuario("juan")
buscar_usuario("maria")

print("\n--- Search products ---")
buscar_producto("SKU001")
buscar_producto("SKU001")

print("\n=== Keys in Redis ===")
for clave in manager.redis_client.keys("app:*"):
    print(f"  {clave.decode() if isinstance(clave, bytes) else clave}")

print(f"\n=== Metrics ===")
print(f"Hits: {metrics.hits}")
print(f"Misses: {metrics.misses}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")

manager.close()
