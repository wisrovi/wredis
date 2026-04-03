"""Patrón de dashboard para métricas de caché.

Este ejemplo muestra cómo construir un panel de monitoreo
que reporta el estado de la caché en intervalos regulares.
"""

import fakeredis
from wredis.decorators import cache, CacheMetrics

redis_client = fakeredis.FakeStrictRedis()
metrics = CacheMetrics()


@cache(ttl=300, prefix="dashboard", redis_client=redis_client, metrics=metrics)
def obtener_datos_widget(widget_id: str) -> dict:
    """Simula obtención de datos para un widget del dashboard."""
    return {"widget": widget_id, "datos": f"datos_del_widget_{widget_id}"}


def imprimir_dashboard(metrics: CacheMetrics, ciclo: int) -> None:
    """Imprime un snapshot del estado de la caché."""
    total = metrics.hits + metrics.misses
    print(f"\n{'=' * 50}")
    print(f"  Dashboard de Caché - Ciclo #{ciclo}")
    print(f"{'=' * 50}")
    print(f"  Hits:          {metrics.hits}")
    print(f"  Misses:        {metrics.misses}")
    print(f"  Errores:       {metrics.errors}")
    print(f"  Total requests:{total}")
    print(f"  Hit Rate:      {metrics.hit_rate:.1f}%")
    print(f"{'=' * 50}")


# Simular ciclos de actividad
widgets = ["ventas", "usuarios", "trafico", "ventas", "usuarios", "ventas"]

for ciclo, widget in enumerate(widgets, 1):
    obtener_datos_widget(widget)
    imprimir_dashboard(metrics, ciclo)

# Resetear métricas para nuevo período
print("\n=== Reset de métricas para nuevo período ===")
metrics.reset()
imprimir_dashboard(metrics, "post-reset")

# Nuevo ciclo con métricas limpias
obtener_datos_widget("ventas")
obtener_datos_widget("ventas")
imprimir_dashboard(metrics, "nuevo período")
