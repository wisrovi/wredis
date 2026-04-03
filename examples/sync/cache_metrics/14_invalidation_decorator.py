"""Decorador de invalidación con métricas.

Este ejemplo muestra cómo combinar @cache con invalidación
de caché y observar el impacto en las métricas.
"""

import fakeredis
from wredis.decorators import cache, invalidate_cache, CacheMetrics

redis_client = fakeredis.FakeStrictRedis()
metrics = CacheMetrics()


@cache(ttl=600, prefix="perfil", redis_client=redis_client, metrics=metrics)
def obtener_perfil_usuario(user_id: int) -> dict:
    """Obtiene el perfil de un usuario."""
    return {"user_id": user_id, "nombre": f"Usuario_{user_id}", "email": f"user{user_id}@test.com"}


@invalidate_cache(pattern="perfil:*", redis_client=redis_client)
def actualizar_perfil(user_id: int, nuevos_datos: dict) -> dict:
    """Actualiza el perfil e invalida la caché."""
    perfil = {"user_id": user_id, **nuevos_datos}
    print(f"  [DB] Perfil actualizado: {perfil}")
    return perfil


# Flujo de trabajo completo
print("=== 1. Obtener perfil (miss) ===")
perfil = obtener_perfil_usuario(1)
print(f"Perfil: {perfil}")
print(f"Métricas: {metrics}")

print("\n=== 2. Obtener perfil nuevamente (hit) ===")
perfil = obtener_perfil_usuario(1)
print(f"Perfil: {perfil}")
print(f"Métricas: {metrics}")

print("\n=== 3. Actualizar perfil (invalida caché) ===")
actualizar_perfil(1, {"nombre": "Usuario_Actualizado"})
print(f"Métricas después de invalidar: {metrics}")

print("\n=== 4. Obtener perfil después de invalidar (miss) ===")
perfil = obtener_perfil_usuario(1)
print(f"Perfil: {perfil}")
print(f"Métricas: {metrics}")

print(f"\n=== Resumen ===")
print(f"Total hits: {metrics.hits}")
print(f"Total misses: {metrics.misses}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")
