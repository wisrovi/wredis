"""Manejo de errores y métricas de error.

Este ejemplo demuestra cómo se registran los errores de caché
en las métricas y cómo la función sigue funcionando.
"""

import unittest.mock

import fakeredis
import redis
from wredis.decorators import cache, CacheMetrics
from wredis._exceptions import CacheError

redis_client = fakeredis.FakeStrictRedis(decode_responses=True)
metrics = CacheMetrics()


@cache(ttl=300, prefix="datos", redis_client=redis_client, metrics=metrics)
def obtener_datos_seguros(key: str) -> dict:
    """Función que funciona incluso si la caché falla."""
    return {"key": key, "valor": f"valor_para_{key}"}


# Operaciones normales
print("=== Operaciones normales ===")
resultado = obtener_datos_seguros("config1")
print(f"Resultado: {resultado}")
print(f"Métricas: {metrics}")

resultado = obtener_datos_seguros("config1")
print(f"Resultado (cache hit): {resultado}")
print(f"Métricas: {metrics}")

# Simular error de caché usando mock para forzar un RedisError
print("\n=== Simulando error de caché ===")
with unittest.mock.patch.object(redis_client, "get", side_effect=redis.RedisError("simulated connection error")):
    try:
        resultado = obtener_datos_seguros("config2")
        print(f"Resultado: {resultado}")
    except CacheError as e:
        print(f"Error de caché capturado: {e}")

print(f"Métricas después del error: {metrics}")
print(f"Errores registrados: {metrics.errors}")

# Resetear métricas
print("\n=== Reset de métricas ===")
metrics.reset()
print(f"Métricas después del reset: {metrics}")
