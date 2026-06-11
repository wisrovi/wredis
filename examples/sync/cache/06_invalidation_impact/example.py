"""Invalidation impact on metrics.

This example demonstrates how cache invalidation affects
metrics and how to track misses caused by invalidation.
"""

from wredis.decorators import CacheMetrics, cache
from wredis.sync import BaseManager

manager = BaseManager(verbose=False)
metrics = CacheMetrics()


@cache(ttl=600, prefix="session", redis_client=manager.redis_client, metrics=metrics)
def obtener_sesion(session_id: str) -> dict:
    """Gets user session data."""
    return {"session_id": session_id, "datos": "datos_de_sesion"}


def invalidar_sesion(session_id: str) -> None:
    """Invalidates a specific session in cache."""
    patron = "session:*"
    claves = manager.redis_client.keys(patron)
    for clave in claves:
        valor = manager.redis_client.get(clave)
        if session_id.encode() in valor:
            manager.redis_client.delete(clave)
            print(f"  [Invalidated] session: {session_id}")
            break


print("=== Normal flow ===")
obtener_sesion("abc123")  # miss
print(f"After first access: {metrics}")

obtener_sesion("abc123")  # hit
print(f"After second access: {metrics}")

print("\n=== Invalidating session ===")
invalidar_sesion("abc123")

print("\n=== After invalidation ===")
obtener_sesion("abc123")  # miss due to invalidation
print(f"After post-invalidation access: {metrics}")

obtener_sesion("abc123")  # hit
print(f"After next access: {metrics}")

print("\n=== Summary ===")
print(f"Hits: {metrics.hits}")
print(f"Misses: {metrics.misses}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")

manager.close()
