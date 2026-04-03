"""Seguimiento básico de métricas de caché.

Este ejemplo demuestra cómo usar CacheMetrics para rastrear
aciertos y fallos de caché en operaciones simples con @cache.
"""

import fakeredis
from wredis.decorators import cache, CacheMetrics

# Crear cliente Redis en memoria para pruebas
redis_client = fakeredis.FakeStrictRedis()

# Instanciar el rastreador de métricas
metrics = CacheMetrics()


@cache(ttl=300, prefix="usuario", redis_client=redis_client, metrics=metrics)
def obtener_usuario(user_id: int) -> dict:
    """Simula una consulta costosa a base de datos."""
    return {"id": user_id, "nombre": f"Usuario_{user_id}"}


# Primera llamada: fallo de caché (miss)
print("=== Primera llamada (miss) ===")
resultado = obtener_usuario(1)
print(f"Resultado: {resultado}")
print(f"Métricas: hits={metrics.hits}, misses={metrics.misses}")
print()

# Segunda llamada: acierto de caché (hit)
print("=== Segunda llamada (hit) ===")
resultado = obtener_usuario(1)
print(f"Resultado: {resultado}")
print(f"Métricas: hits={metrics.hits}, misses={metrics.misses}")
print()

# Tercera llamada con diferente argumento: otro miss
print("=== Tercera llamada con otro ID (miss) ===")
resultado = obtener_usuario(2)
print(f"Resultado: {resultado}")
print(f"Métricas: hits={metrics.hits}, misses={metrics.misses}")
print()

# Resumen final
print(f"=== Resumen ===")
print(f"Métricas finales: {metrics}")
print(f"Tasa de aciertos: {metrics.hit_rate:.1f}%")
