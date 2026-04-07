"""Performance comparison with and without cache.

This example compares execution time of functions
with and without cache, showing the impact on metrics.
"""

import time

from wredis.decorators import CacheMetrics, cache
from wredis.sync import BaseManager

manager = BaseManager(verbose=False)
metrics = CacheMetrics()


def operacion_costosa_sin_cache(n: int) -> int:
    """Expensive operation without cache."""
    time.sleep(0.01)  # Simulate processing
    return sum(i * i for i in range(n))


@cache(ttl=600, prefix="benchmark", redis_client=manager.redis_client, metrics=metrics)
def operacion_costosa_con_cache(n: int) -> int:
    """Same operation but with cache."""
    time.sleep(0.01)  # Simulate processing
    return sum(i * i for i in range(n))


print("=== Without cache ===")
inicio = time.time()
for _ in range(5):
    operacion_costosa_sin_cache(1000)
tiempo_sin_cache = time.time() - inicio
print(f"Total time: {tiempo_sin_cache:.4f}s")

print("\n=== With cache ===")
inicio = time.time()
for _ in range(5):
    operacion_costosa_con_cache(1000)
tiempo_con_cache = time.time() - inicio
print(f"Total time: {tiempo_con_cache:.4f}s")

print(f"\n=== Cache metrics ===")
print(f"Hits: {metrics.hits}")
print(f"Misses: {metrics.misses}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")
print(f"Performance improvement: {tiempo_sin_cache / tiempo_con_cache:.1f}x faster")

manager.close()
