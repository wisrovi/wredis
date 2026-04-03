"""Alertas por baja tasa de aciertos.

Este ejemplo implementa un sistema de alertas que se activa
cuando la tasa de aciertos de caché cae por debajo de un umbral.
"""

import fakeredis
from wredis.decorators import cache, CacheMetrics

redis_client = fakeredis.FakeStrictRedis()
metrics = CacheMetrics()

# Umbral mínimo aceptable de hit rate
UMBRAL_ALERTA = 50.0


@cache(ttl=300, prefix="api", redis_client=redis_client, metrics=metrics)
def consultar_api(endpoint: str) -> dict:
    """Simula consulta a API externa."""
    return {"endpoint": endpoint, "respuesta": "datos_api"}


def verificar_alerta(metrics: CacheMetrics, umbral: float) -> None:
    """Verifica si la tasa de aciertos está por debajo del umbral."""
    if metrics.hits + metrics.misses == 0:
        print("  [INFO] Aún no hay datos suficientes para evaluar")
        return

    if metrics.hit_rate < umbral:
        print(f"  [ALERTA] Hit rate {metrics.hit_rate:.1f}% < {umbral}% - Posible problema de caché")
    else:
        print(f"  [OK] Hit rate {metrics.hit_rate:.1f}% >= {umbral}% - Caché saludable")


# Simular escenario con hit rate bajo (muchos endpoints únicos)
print("=== Escenario 1: Acceso a muchos endpoints únicos ===")
endpoints_unicos = [f"/api/recurso/{i}" for i in range(5)]
for ep in endpoints_unicos:
    consultar_api(ep)
    verificar_alerta(metrics, UMBRAL_ALERTA)

# Resetear y simular escenario saludable
metrics.reset()
print("\n=== Escenario 2: Acceso repetido a pocos endpoints ===")
endpoints_repetidos = ["/api/usuarios", "/api/usuarios", "/api/usuarios", "/api/productos", "/api/productos"]
for ep in endpoints_repetidos:
    consultar_api(ep)
    verificar_alerta(metrics, UMBRAL_ALERTA)

print(f"\n=== Resumen final ===")
print(f"Métricas: {metrics}")
