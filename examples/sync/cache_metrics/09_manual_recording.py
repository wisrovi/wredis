"""Registro manual de hits y misses.

Este ejemplo demuestra cómo usar record_hit(), record_miss() y
record_error() para rastrear operaciones de caché manuales.
"""

import fakeredis
from wredis.decorators import CacheMetrics

# Crear instancia de métricas para uso manual
metrics = CacheMetrics()


def obtener_de_cache_manual(clave: str, redis_client) -> str | None:
    """Intenta obtener un valor de caché manualmente."""
    try:
        valor = redis_client.get(clave)
        if valor is not None:
            metrics.record_hit()
            return valor.decode()
        else:
            metrics.record_miss()
            return None
    except Exception:
        metrics.record_error()
        return None


def guardar_en_cache_manual(clave: str, valor: str, redis_client, ttl: int = 300) -> None:
    """Guarda un valor en caché manualmente."""
    redis_client.setex(clave, ttl, valor)


redis_client = fakeredis.FakeStrictRedis()

# Simular flujo de caché manual
print("=== Operaciones manuales de caché ===")

# Primer intento: miss
resultado = obtener_de_cache_manual("config:app_name", redis_client)
print(f"Intento 1 (miss): {resultado}")

# Guardar en caché
guardar_en_cache_manual("config:app_name", "MiAplicacion", redis_client)
print("  -> Guardado en caché")

# Segundo intento: hit
resultado = obtener_de_cache_manual("config:app_name", redis_client)
print(f"Intento 2 (hit): {resultado}")

# Tercer intento: hit
resultado = obtener_de_cache_manual("config:app_name", redis_client)
print(f"Intento 3 (hit): {resultado}")

# Intento con clave inexistente: miss
resultado = obtener_de_cache_manual("config:inexistente", redis_client)
print(f"Intento 4 (miss): {resultado}")

print(f"\n=== Métricas finales ===")
print(f"Hits: {metrics.hits}")
print(f"Misses: {metrics.misses}")
print(f"Errores: {metrics.errors}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")
print(f"Total: {metrics}")
