"""Dashboard pattern for cache metrics.

This example shows how to build a monitoring dashboard
that reports cache status at regular intervals.
"""

from wredis.decorators import CacheMetrics, cache
from wredis.sync import BaseManager

manager = BaseManager(verbose=False)
metrics = CacheMetrics()


@cache(ttl=300, prefix="dashboard", redis_client=manager.redis_client, metrics=metrics)
def obtener_datos_widget(widget_id: str) -> dict:
    """Simulates fetching data for a dashboard widget."""
    return {"widget": widget_id, "datos": f"datos_del_widget_{widget_id}"}


def imprimir_dashboard(metrics: CacheMetrics, ciclo: int) -> None:
    """Prints a snapshot of cache status."""
    total = metrics.hits + metrics.misses
    print(f"\n{'=' * 50}")
    print(f"  Cache Dashboard - Cycle #{ciclo}")
    print(f"{'=' * 50}")
    print(f"  Hits:          {metrics.hits}")
    print(f"  Misses:        {metrics.misses}")
    print(f"  Errors:        {metrics.errors}")
    print(f"  Total requests:{total}")
    print(f"  Hit Rate:      {metrics.hit_rate:.1f}%")
    print(f"{'=' * 50}")


widgets = ["ventas", "usuarios", "trafico", "ventas", "usuarios", "ventas"]

for ciclo, widget in enumerate(widgets, 1):
    obtener_datos_widget(widget)
    imprimir_dashboard(metrics, ciclo)

print("\n=== Metrics reset for new period ===")
metrics.reset()
imprimir_dashboard(metrics, "post-reset")

obtener_datos_widget("ventas")
obtener_datos_widget("ventas")
imprimir_dashboard(metrics, "new period")

manager.close()
