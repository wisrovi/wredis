"""Métricas con prefijos personalizados y key builders.

Este ejemplo muestra cómo usar prefijos personalizados y funciones
personalizadas para construir claves de caché junto con métricas.
"""

import fakeredis
from wredis.decorators import cache, CacheMetrics

redis_client = fakeredis.FakeStrictRedis()
metrics = CacheMetrics()


def mi_key_builder(func, args, kwargs) -> str:
    """Constructor personalizado de claves de caché."""
    # Usar solo el primer argumento como clave
    return f"custom:{func.__name__}:{args[0]}"


@cache(ttl=300, prefix="app", key_builder=mi_key_builder, redis_client=redis_client, metrics=metrics)
def buscar_usuario(username: str) -> dict:
    """Busca usuario por nombre de usuario."""
    return {"username": username, "email": f"{username}@ejemplo.com"}


@cache(ttl=300, prefix="app", key_builder=mi_key_builder, redis_client=redis_client, metrics=metrics)
def buscar_producto(sku: str) -> dict:
    """Busca producto por SKU."""
    return {"sku": sku, "nombre": f"Producto_{sku}"}


# Probar con claves personalizadas
print("=== Búsquedas con key builder personalizado ===")

print("\n--- Buscar usuarios ---")
buscar_usuario("juan")  # miss -> clave: app:custom:buscar_usuario:juan
buscar_usuario("juan")  # hit
buscar_usuario("maria")  # miss -> clave: app:custom:buscar_usuario:maria

print("\n--- Buscar productos ---")
buscar_producto("SKU001")  # miss -> clave: app:custom:buscar_producto:SKU001
buscar_producto("SKU001")  # hit

# Verificar las claves creadas en Redis
print("\n=== Claves en Redis ===")
for clave in redis_client.keys("app:*"):
    print(f"  {clave.decode()}")

print(f"\n=== Métricas ===")
print(f"Hits: {metrics.hits}")
print(f"Misses: {metrics.misses}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")
