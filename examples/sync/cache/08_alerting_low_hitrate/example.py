"""Alerting on low hit rate.

This example implements an alerting system that triggers
when cache hit rate falls below a threshold.
"""

from wredis.decorators import CacheMetrics, cache
from wredis.sync import BaseManager

manager = BaseManager(verbose=False)
metrics = CacheMetrics()

ALERT_THRESHOLD = 50.0


@cache(ttl=300, prefix="api", redis_client=manager.redis_client, metrics=metrics)
def consultar_api(endpoint: str) -> dict:
    """Simulates external API query."""
    return {"endpoint": endpoint, "respuesta": "datos_api"}


def verificar_alerta(metrics: CacheMetrics, umbral: float) -> None:
    """Checks if hit rate is below threshold."""
    if metrics.hits + metrics.misses == 0:
        print("  [INFO] Not enough data yet to evaluate")
        return

    if metrics.hit_rate < umbral:
        print(
            f"  [ALERT] Hit rate {metrics.hit_rate:.1f}% < {umbral}% - Possible cache problem"
        )
    else:
        print(f"  [OK] Hit rate {metrics.hit_rate:.1f}% >= {umbral}% - Cache healthy")


print("=== Scenario 1: Access to many unique endpoints ===")
endpoints_unicos = [f"/api/recurso/{i}" for i in range(5)]
for ep in endpoints_unicos:
    consultar_api(ep)
    verificar_alerta(metrics, ALERT_THRESHOLD)

metrics.reset()
print("\n=== Scenario 2: Repeated access to few endpoints ===")
endpoints_repetidos = [
    "/api/usuarios",
    "/api/usuarios",
    "/api/usuarios",
    "/api/productos",
    "/api/productos",
]
for ep in endpoints_repetidos:
    consultar_api(ep)
    verificar_alerta(metrics, ALERT_THRESHOLD)

print(f"\n=== Final Summary ===")
print(f"Metrics: {metrics}")

manager.close()
