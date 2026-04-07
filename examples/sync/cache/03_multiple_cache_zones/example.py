"""Multiple cache zones with separate metrics.

This example demonstrates how to use independent CacheMetrics instances
to track different cache zones or categories.
"""

from wredis.decorators import CacheMetrics, cache
from wredis.sync import BaseManager

manager = BaseManager(verbose=False)

metrics_usuarios = CacheMetrics()
metrics_productos = CacheMetrics()
metrics_pedidos = CacheMetrics()


@cache(
    ttl=300,
    prefix="usuarios",
    redis_client=manager.redis_client,
    metrics=metrics_usuarios,
)
def obtener_usuario(user_id: int) -> dict:
    """Simulated user table query."""
    return {"id": user_id, "nombre": f"User_{user_id}"}


@cache(
    ttl=300,
    prefix="productos",
    redis_client=manager.redis_client,
    metrics=metrics_productos,
)
def obtener_producto(prod_id: int) -> dict:
    """Simulated products table query."""
    return {"id": prod_id, "nombre": f"Prod_{prod_id}"}


@cache(
    ttl=300,
    prefix="pedidos",
    redis_client=manager.redis_client,
    metrics=metrics_pedidos,
)
def obtener_pedido(order_id: int) -> dict:
    """Simulated orders table query."""
    return {"id": order_id, "total": order_id * 25.0}


print("=== Users Zone ===")
obtener_usuario(1)  # miss
obtener_usuario(1)  # hit
obtener_usuario(2)  # miss
print(f"Users metrics: {metrics_usuarios}")

print("\n=== Products Zone ===")
obtener_producto(10)  # miss
obtener_producto(10)  # hit
obtener_producto(10)  # hit
obtener_producto(11)  # miss
print(f"Products metrics: {metrics_productos}")

print("\n=== Orders Zone ===")
obtener_pedido(100)  # miss
obtener_pedido(100)  # hit
print(f"Orders metrics: {metrics_pedidos}")

print("\n=== Zone Comparison ===")
print(f"{'Zone':<15} {'Hits':>6} {'Misses':>8} {'Hit Rate':>10}")
for nombre, m in [
    ("Users", metrics_usuarios),
    ("Products", metrics_productos),
    ("Orders", metrics_pedidos),
]:
    print(f"{nombre:<15} {m.hits:>6} {m.misses:>8} {m.hit_rate:>9.1f}%")

manager.close()
