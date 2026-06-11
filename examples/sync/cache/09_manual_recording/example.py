"""Manual hit and miss recording.

This example demonstrates how to use record_hit(), record_miss() and
record_error() to track manual cache operations.
"""

from wredis.decorators import CacheMetrics
from wredis.sync import BaseManager

manager = BaseManager(verbose=False)
metrics = CacheMetrics()


def obtener_de_cache_manual(clave: str, redis_client) -> str | None:
    """Attempts to get a value from cache manually."""
    try:
        valor = redis_client.get(clave)
        if valor is not None:
            metrics.record_hit()
            return valor.decode() if isinstance(valor, bytes) else valor
        else:
            metrics.record_miss()
            return None
    except Exception:
        metrics.record_error()
        return None


def guardar_en_cache_manual(clave: str, valor: str, redis_client, ttl: int = 300) -> None:
    """Manually saves a value to cache."""
    redis_client.setex(clave, ttl, valor)


print("=== Manual cache operations ===")

resultado = obtener_de_cache_manual("config:app_name", manager.redis_client)
print(f"Attempt 1 (miss): {resultado}")

guardar_en_cache_manual("config:app_name", "MiAplicacion", manager.redis_client)
print("  -> Saved to cache")

resultado = obtener_de_cache_manual("config:app_name", manager.redis_client)
print(f"Attempt 2 (hit): {resultado}")

resultado = obtener_de_cache_manual("config:app_name", manager.redis_client)
print(f"Attempt 3 (hit): {resultado}")

resultado = obtener_de_cache_manual("config:inexistente", manager.redis_client)
print(f"Attempt 4 (miss): {resultado}")

print("\n=== Final Metrics ===")
print(f"Hits: {metrics.hits}")
print(f"Misses: {metrics.misses}")
print(f"Errors: {metrics.errors}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")
print(f"Total: {metrics}")

manager.close()
