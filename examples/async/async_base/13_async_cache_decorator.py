"""13 - Decorador de caché asíncrona

Este ejemplo implementa un decorador personalizado que usa
AsyncBaseManager para cachear resultados de funciones asíncronas,
evitando ejecuciones redundantes con un TTL configurable.
"""

import asyncio
import functools
from typing import Any, Callable

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager

# Manager global compartido para el decorador
_cache_manager: AsyncBaseManager | None = None


def async_cache(ttl: int = 300, prefix: str = "cache"):
    """Decorador para cachear resultados de funciones asíncronas.

    Args:
        ttl: Tiempo de vida del cache en segundos.
        prefix: Prefijo para las claves de cache.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            global _cache_manager
            if _cache_manager is None:
                raise RuntimeError("Cache manager no inicializado")

            # Generamos una clave única basada en los argumentos
            key_args = "_".join(str(a) for a in args)
            key_kwargs = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = f"{prefix}:{func.__name__}:{key_args}:{key_kwargs}"

            # Intentamos obtener del cache
            resultado_cache = await _cache_manager._execute("get", cache_key)
            if resultado_cache is not None:
                print(f"  [CACHE HIT] {cache_key}")
                return resultado_cache

            # Ejecutamos la función
            print(f"  [CACHE MISS] {cache_key} - ejecutando función")
            resultado = await func(*args, **kwargs)

            # Guardamos en cache
            await _cache_manager._execute("set", cache_key, str(resultado), ex=ttl)
            return resultado

        return wrapper

    return decorator


# Función simulada costosa
@async_cache(ttl=60, prefix="app")
async def calcular_estadisticas(id_reporte: int):
    """Simula un cálculo costoso que se beneficia del cache."""
    await asyncio.sleep(0.1)  # Simula procesamiento
    return f"estadisticas_del_reporte_{id_reporte}"


async def main():
    global _cache_manager

    # Creamos un FakeRedis para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async with AsyncBaseManager(verbose=False) as manager:
        manager.redis_client = fake
        _cache_manager = manager

        print("=== Primera llamada (CACHE MISS) ===")
        resultado1 = await calcular_estadisticas(42)
        print(f"  Resultado: {resultado1}")

        print("\n=== Segunda llamada igual (CACHE HIT) ===")
        resultado2 = await calcular_estadisticas(42)
        print(f"  Resultado: {resultado2}")

        print("\n=== Tercera llamada con args distintos (CACHE MISS) ===")
        resultado3 = await calcular_estadisticas(99)
        print(f"  Resultado: {resultado3}")

        print("\n=== Cuarta llamada igual a la primera (CACHE HIT) ===")
        resultado4 = await calcular_estadisticas(42)
        print(f"  Resultado: {resultado4}")

        # Verificamos las claves en cache
        print("\n=== Claves en cache ===")
        claves = await manager._execute("keys", "app:*")
        for clave in sorted(claves):
            valor = await manager._execute("get", clave)
            ttl = await manager._execute("ttl", clave)
            print(f"  {clave} = {valor} (TTL: {ttl}s)")

    _cache_manager = None
    await fake.aclose()
    print("\nDecorador de caché completado")


if __name__ == "__main__":
    asyncio.run(main())
