"""Métricas con funciones asíncronas usando @async_cache.

Este ejemplo muestra cómo usar CacheMetrics con el decorador
async_cache para funciones asíncronas.
"""

import asyncio
import fakeredis
import redis.asyncio as aredis
from wredis.decorators import async_cache, CacheMetrics


async def main():
    # Crear cliente Redis asíncrono en memoria
    redis_client = aredis.Redis()
    metrics = CacheMetrics()

    @async_cache(ttl=300, prefix="async_data", redis_client=redis_client, metrics=metrics)
    async def obtener_datos_async(item_id: int) -> dict:
        """Simula operación asíncrona costosa."""
        await asyncio.sleep(0.01)  # Simular latencia de red
        return {"id": item_id, "datos": f"datos_async_{item_id}"}

    # Primera llamada: miss
    print("=== Primera llamada (miss) ===")
    resultado = await obtener_datos_async(1)
    print(f"Resultado: {resultado}")
    print(f"Métricas: hits={metrics.hits}, misses={metrics.misses}")

    # Segunda llamada: hit
    print("\n=== Segunda llamada (hit) ===")
    resultado = await obtener_datos_async(1)
    print(f"Resultado: {resultado}")
    print(f"Métricas: hits={metrics.hits}, misses={metrics.misses}")

    # Múltiples llamadas
    print("\n=== Múltiples llamadas ===")
    for i in [2, 1, 3, 1, 2]:
        await obtener_datos_async(i)

    print(f"\n=== Resumen final ===")
    print(f"Métricas: {metrics}")
    print(f"Hit rate: {metrics.hit_rate:.1f}%")

    await redis_client.close()


asyncio.run(main())
