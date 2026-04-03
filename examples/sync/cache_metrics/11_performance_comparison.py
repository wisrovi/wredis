"""Comparación de rendimiento con y sin caché.

Este ejemplo compara el tiempo de ejecución de funciones
con y sin caché, mostrando el impacto en métricas.
"""

import time
import fakeredis
from wredis.decorators import cache, CacheMetrics

redis_client = fakeredis.FakeStrictRedis()
metrics = CacheMetrics()


def operacion_costosa_sin_cache(n: int) -> int:
    """Operación costosa sin caché."""
    time.sleep(0.01)  # Simular procesamiento
    return sum(i * i for i in range(n))


@cache(ttl=600, prefix="benchmark", redis_client=redis_client, metrics=metrics)
def operacion_costosa_con_cache(n: int) -> int:
    """Misma operación pero con caché."""
    time.sleep(0.01)  # Simular procesamiento
    return sum(i * i for i in range(n))


# Benchmark sin caché
print("=== Sin caché ===")
inicio = time.time()
for _ in range(5):
    operacion_costosa_sin_cache(1000)
tiempo_sin_cache = time.time() - inicio
print(f"Tiempo total: {tiempo_sin_cache:.4f}s")

# Benchmark con caché
print("\n=== Con caché ===")
inicio = time.time()
for _ in range(5):
    operacion_costosa_con_cache(1000)
tiempo_con_cache = time.time() - inicio
print(f"Tiempo total: {tiempo_con_cache:.4f}s")

# Métricas de caché
print(f"\n=== Métricas de caché ===")
print(f"Hits: {metrics.hits}")
print(f"Misses: {metrics.misses}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")
print(f"Mejora de rendimiento: {tiempo_sin_cache / tiempo_con_cache:.1f}x más rápido")
