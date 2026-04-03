"""Monitoreo de tasa de aciertos (hit rate).

Este ejemplo muestra cómo calcular y monitorear la tasa de aciertos
de caché usando la propiedad hit_rate de CacheMetrics.
"""

import fakeredis
from wredis.decorators import cache, CacheMetrics

redis_client = fakeredis.FakeStrictRedis()
metrics = CacheMetrics()


@cache(ttl=600, prefix="producto", redis_client=redis_client, metrics=metrics)
def obtener_producto(producto_id: int) -> dict:
    """Simula consulta a catálogo de productos."""
    return {"id": producto_id, "nombre": f"Producto_{producto_id}", "precio": producto_id * 10.5}


# Simular patrón de acceso: algunos accesos repetidos, otros únicos
patron_acceso = [1, 2, 1, 3, 1, 2, 4, 1, 5, 1]

for i, pid in enumerate(patron_acceso, 1):
    resultado = obtener_producto(pid)
    print(f"Acceso #{i}: producto_id={pid} -> {resultado['nombre']}")
    print(f"  Hit rate actual: {metrics.hit_rate:.1f}%")

print()
print("=== Resumen final ===")
print(f"Total hits: {metrics.hits}")
print(f"Total misses: {metrics.misses}")
print(f"Total errores: {metrics.errors}")
print(f"Tasa de aciertos: {metrics.hit_rate:.1f}%")
print(f"Representación: {metrics}")
