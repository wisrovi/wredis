"""Cache warming.

This example shows how to pre-warm the cache with known data
before real requests arrive, improving hit rate.
"""

from wredis.decorators import CacheMetrics, cache
from wredis.sync import BaseManager

manager = BaseManager(verbose=False)
metrics = CacheMetrics()


@cache(ttl=600, prefix="config", redis_client=manager.redis_client, metrics=metrics)
def cargar_configuracion(clave: str) -> dict:
    """Simulates loading configuration from database."""
    print(f"  [DB] Loading configuration: {clave}")
    return {"clave": clave, "valor": f"valor_para_{clave}"}


print("=== Pre-warming cache ===")
claves_comunes = ["theme", "language", "timezone", "notifications", "layout"]
for clave in claves_comunes:
    cargar_configuracion(clave)

print(f"Metrics after pre-warming: {metrics}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")

print("\n=== Real traffic ===")
solicitudes_reales = ["theme", "language", "theme", "notifications", "theme", "layout"]
for clave in solicitudes_reales:
    resultado = cargar_configuracion(clave)
    print(f"  Request '{clave}' -> {resultado['valor']}")

print(f"\nFinal metrics: {metrics}")
print(f"Final hit rate: {metrics.hit_rate:.1f}%")
print(
    f"Warming benefit: {metrics.hits} hits out of {metrics.hits + metrics.misses} requests"
)

manager.close()
