"""Impacto de la invalidación en las métricas.

Este ejemplo demuestra cómo la invalidación de caché afecta
las métricas y cómo rastrear misses causados por invalidación.
"""

import fakeredis
from wredis.decorators import cache, CacheMetrics

redis_client = fakeredis.FakeStrictRedis()
metrics = CacheMetrics()


@cache(ttl=600, prefix="sesion", redis_client=redis_client, metrics=metrics)
def obtener_sesion(session_id: str) -> dict:
    """Obtiene datos de sesión del usuario."""
    return {"session_id": session_id, "datos": "datos_de_sesion"}


def invalidar_sesion(session_id: str) -> None:
    """Invalida una sesión específica en caché."""
    patron = f"sesion:*"
    claves = redis_client.keys(patron)
    # Invalidar solo la clave específica
    for clave in claves:
        valor = redis_client.get(clave)
        if session_id.encode() in valor:
            redis_client.delete(clave)
            print(f"  [Invalidada] sesión: {session_id}")
            break


# Flujo normal: miss -> hit -> hit
print("=== Flujo normal ===")
obtener_sesion("abc123")  # miss
print(f"Después del primer acceso: {metrics}")

obtener_sesion("abc123")  # hit
print(f"Después del segundo acceso: {metrics}")

# Invalidar la sesión
print("\n=== Invalidando sesión ===")
invalidar_sesion("abc123")

# El siguiente acceso será un miss nuevamente
print("\n=== Después de invalidar ===")
obtener_sesion("abc123")  # miss por invalidación
print(f"Después de acceso post-invalidación: {metrics}")

obtener_sesion("abc123")  # hit
print(f"Después del siguiente acceso: {metrics}")

print(f"\n=== Resumen ===")
print(f"Hits: {metrics.hits}")
print(f"Misses: {metrics.misses}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")
