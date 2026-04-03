"""Múltiples zonas de caché con métricas separadas.

Este ejemplo demuestra cómo usar instancias independientes de
CacheMetrics para rastrear diferentes zonas o categorías de caché.
"""

import fakeredis
from wredis.decorators import cache, CacheMetrics

redis_client = fakeredis.FakeStrictRedis()

# Crear métricas separadas para cada zona de caché
metrics_usuarios = CacheMetrics()
metrics_productos = CacheMetrics()
metrics_pedidos = CacheMetrics()


@cache(ttl=300, prefix="usuarios", redis_client=redis_client, metrics=metrics_usuarios)
def obtener_usuario(user_id: int) -> dict:
    """Consulta simulada a tabla de usuarios."""
    return {"id": user_id, "nombre": f"User_{user_id}"}


@cache(ttl=300, prefix="productos", redis_client=redis_client, metrics=metrics_productos)
def obtener_producto(prod_id: int) -> dict:
    """Consulta simulada a tabla de productos."""
    return {"id": prod_id, "nombre": f"Prod_{prod_id}"}


@cache(ttl=300, prefix="pedidos", redis_client=redis_client, metrics=metrics_pedidos)
def obtener_pedido(order_id: int) -> dict:
    """Consulta simulada a tabla de pedidos."""
    return {"id": order_id, "total": order_id * 25.0}


# Acceder a cada zona de caché
print("=== Zona Usuarios ===")
obtener_usuario(1)  # miss
obtener_usuario(1)  # hit
obtener_usuario(2)  # miss
print(f"Métricas usuarios: {metrics_usuarios}")

print("\n=== Zona Productos ===")
obtener_producto(10)  # miss
obtener_producto(10)  # hit
obtener_producto(10)  # hit
obtener_producto(11)  # miss
print(f"Métricas productos: {metrics_productos}")

print("\n=== Zona Pedidos ===")
obtener_pedido(100)  # miss
obtener_pedido(100)  # hit
print(f"Métricas pedidos: {metrics_pedidos}")

# Comparativa de zonas
print("\n=== Comparativa de zonas ===")
print(f"{'Zona':<15} {'Hits':>6} {'Misses':>8} {'Hit Rate':>10}")
for nombre, m in [("Usuarios", metrics_usuarios), ("Productos", metrics_productos), ("Pedidos", metrics_pedidos)]:
    print(f"{nombre:<15} {m.hits:>6} {m.misses:>8} {m.hit_rate:>9.1f}%")
