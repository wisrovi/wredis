"""Invalidation decorator with metrics.

This example shows how to combine @cache with cache
invalidation and observe the impact on metrics.
"""

from wredis.decorators import CacheMetrics, cache, invalidate_cache
from wredis.sync import BaseManager

manager = BaseManager(verbose=False)
metrics = CacheMetrics()


@cache(ttl=600, prefix="perfil", redis_client=manager.redis_client, metrics=metrics)
def obtener_perfil_usuario(user_id: int) -> dict:
    """Gets user profile."""
    return {
        "user_id": user_id,
        "nombre": f"Usuario_{user_id}",
        "email": f"user{user_id}@test.com",
    }


@invalidate_cache(pattern="perfil:*", redis_client=manager.redis_client)
def actualizar_perfil(user_id: int, nuevos_datos: dict) -> dict:
    """Updates profile and invalidates cache."""
    perfil = {"user_id": user_id, **nuevos_datos}
    print(f"  [DB] Profile updated: {perfil}")
    return perfil


print("=== 1. Get profile (miss) ===")
perfil = obtener_perfil_usuario(1)
print(f"Profile: {perfil}")
print(f"Metrics: {metrics}")

print("\n=== 2. Get profile again (hit) ===")
perfil = obtener_perfil_usuario(1)
print(f"Profile: {perfil}")
print(f"Metrics: {metrics}")

print("\n=== 3. Update profile (invalidates cache) ===")
actualizar_perfil(1, {"nombre": "Usuario_Actualizado"})
print(f"Metrics after invalidation: {metrics}")

print("\n=== 4. Get profile after invalidation (miss) ===")
perfil = obtener_perfil_usuario(1)
print(f"Profile: {perfil}")
print(f"Metrics: {metrics}")

print(f"\n=== Summary ===")
print(f"Total hits: {metrics.hits}")
print(f"Total misses: {metrics.misses}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")

manager.close()
