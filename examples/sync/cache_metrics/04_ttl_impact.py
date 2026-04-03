"""Impacto del TTL en la tasa de aciertos.

Este ejemplo compara cómo diferentes valores de TTL afectan
la tasa de aciertos de caché en un escenario simulado.
"""

import fakeredis
from wredis.decorators import cache, CacheMetrics

# Escenario 1: TTL muy corto (1 segundo)
redis_corto = fakeredis.FakeStrictRedis()
metrics_corto = CacheMetrics()


@cache(ttl=1, prefix="datos_cortos", redis_client=redis_corto, metrics=metrics_corto)
def consulta_corta(query_id: int) -> dict:
    """Consulta con caché de vida muy corta."""
    return {"query": query_id, "resultado": "datos_procesados"}


# Escenario 2: TTL largo (3600 segundos)
redis_largo = fakeredis.FakeStrictRedis()
metrics_largo = CacheMetrics()


@cache(ttl=3600, prefix="datos_largos", redis_client=redis_largo, metrics=metrics_largo)
def consulta_larga(query_id: int) -> dict:
    """Consulta con caché de vida larga."""
    return {"query": query_id, "resultado": "datos_procesados"}


# Simular accesos espaciados en el tiempo
print("=== TTL Corto (1 segundo) ===")
for i in range(5):
    consulta_corta(1)
    # Simular paso del tiempo avanzando el reloj de fakeredis
    redis_corto.time = lambda: (1700000000 + i * 2, 0)
    print(f"  Acceso {i + 1}: hits={metrics_corto.hits}, misses={metrics_corto.misses}")

print(f"Hit rate final: {metrics_corto.hit_rate:.1f}%")

print("\n=== TTL Largo (3600 segundos) ===")
for i in range(5):
    consulta_larga(1)
    redis_largo.time = lambda: (1700000000 + i * 2, 0)
    print(f"  Acceso {i + 1}: hits={metrics_largo.hits}, misses={metrics_largo.misses}")

print(f"Hit rate final: {metrics_largo.hit_rate:.1f}%")

print("\n=== Comparación ===")
print(f"TTL corto -> Hit rate: {metrics_corto.hit_rate:.1f}%")
print(f"TTL largo -> Hit rate: {metrics_largo.hit_rate:.1f}%")
