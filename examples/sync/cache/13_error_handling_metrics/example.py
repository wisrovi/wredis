"""Error handling and error metrics.

This example demonstrates how cache errors are recorded
in metrics and how the function continues to work.
"""

import unittest.mock

from wredis._exceptions import CacheError
from wredis.decorators import CacheMetrics, cache
from wredis.sync import BaseManager

manager = BaseManager(verbose=False)
metrics = CacheMetrics()


@cache(ttl=300, prefix="datos", redis_client=manager.redis_client, metrics=metrics)
def obtener_datos_seguros(key: str) -> dict:
    """Function that works even if cache fails."""
    return {"key": key, "valor": f"valor_para_{key}"}


print("=== Normal operations ===")
resultado = obtener_datos_seguros("config1")
print(f"Result: {resultado}")
print(f"Metrics: {metrics}")

resultado = obtener_datos_seguros("config1")
print(f"Result (cache hit): {resultado}")
print(f"Metrics: {metrics}")

print("\n=== Simulating cache error ===")
with unittest.mock.patch.object(
    manager.redis_client, "get", side_effect=Exception("simulated connection error")
):
    try:
        resultado = obtener_datos_seguros("config2")
        print(f"Result: {resultado}")
    except CacheError as e:
        print(f"Cache error captured: {e}")

print(f"Metrics after error: {metrics}")
print(f"Errors recorded: {metrics.errors}")

print("\n=== Metrics reset ===")
metrics.reset()
print(f"Metrics after reset: {metrics}")

manager.close()
