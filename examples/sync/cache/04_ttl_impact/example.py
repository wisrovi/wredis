"""TTL impact on hit rate.

This example compares how different TTL values affect
cache hit rate in a simulated scenario.
"""

import time

from wredis.decorators import CacheMetrics, cache
from wredis.sync import BaseManager

manager = BaseManager(verbose=False)

metrics_corto = CacheMetrics()
metrics_largo = CacheMetrics()


@cache(
    ttl=1,
    prefix="datos_cortos",
    redis_client=manager.redis_client,
    metrics=metrics_corto,
)
def consulta_corta(query_id: int) -> dict:
    """Query with very short cache lifetime."""
    return {"query": query_id, "resultado": "datos_procesados"}


@cache(
    ttl=10,
    prefix="datos_largos",
    redis_client=manager.redis_client,
    metrics=metrics_largo,
)
def consulta_larga(query_id: int) -> dict:
    """Query with long cache lifetime."""
    return {"query": query_id, "resultado": "datos_procesados"}


print("=== Short TTL (1 second) ===")
for i in range(5):
    consulta_corta(1)
    print(f"  Access {i + 1}: hits={metrics_corto.hits}, misses={metrics_corto.misses}")
    time.sleep(1.1)

print(f"Final hit rate: {metrics_corto.hit_rate:.1f}%")

print("\n=== Long TTL (10 seconds) ===")
for i in range(5):
    consulta_larga(1)
    print(f"  Access {i + 1}: hits={metrics_largo.hits}, misses={metrics_largo.misses}")
    time.sleep(0.5)

print(f"Final hit rate: {metrics_largo.hit_rate:.1f}%")

print("\n=== Comparison ===")
print(f"Short TTL -> Hit rate: {metrics_corto.hit_rate:.1f}%")
print(f"Long TTL -> Hit rate: {metrics_largo.hit_rate:.1f}%")

manager.close()
