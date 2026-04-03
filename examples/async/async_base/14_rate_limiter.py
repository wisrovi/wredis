"""14 - Rate Limiter asíncrono

Este ejemplo implementa un rate limiter (limitador de tasa) usando
Redis con el algoritmo de sliding window log, aprovechando las
operaciones asíncronas de AsyncBaseManager.
"""

import asyncio
import time
from typing import Any

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager


class RateLimiter:
    """Limitador de tasa usando Redis con sliding window log."""

    def __init__(self, manager: AsyncBaseManager, max_requests: int, window_seconds: int):
        """Inicializa el rate limiter.

        Args:
            manager: Instancia de AsyncBaseManager.
            max_requests: Número máximo de peticiones permitidas.
            window_seconds: Ventana de tiempo en segundos.
        """
        self.manager = manager
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def is_allowed(self, client_id: str) -> tuple[bool, dict[str, Any]]:
        """Verifica si una petición está permitida.

        Args:
            client_id: Identificador único del cliente.

        Returns:
            Tupla con (permitido, info_del_limiter).
        """
        key = f"ratelimit:{client_id}"
        ahora = time.time()
        ventana_inicio = ahora - self.window_seconds

        # Eliminamos entradas fuera de la ventana
        await self.manager._execute("zremrangebyscore", key, 0, ventana_inicio)

        # Contamos peticiones en la ventana actual
        contador = await self.manager._execute("zcard", key)

        if contador < self.max_requests:
            # Petición permitida - registramos timestamp
            await self.manager._execute("zadd", key, {str(ahora): ahora})
            await self.manager._execute("expire", key, self.window_seconds)
            return True, {
                "permitido": True,
                "peticiones_usadas": contador + 1,
                "peticiones_restantes": self.max_requests - contador - 1,
                "ventana_segundos": self.window_seconds,
            }
        else:
            # Petición denegada
            return False, {
                "permitido": False,
                "peticiones_usadas": contador,
                "peticiones_restantes": 0,
                "ventana_segundos": self.window_seconds,
            }


async def main():
    # Creamos un FakeRedis para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async with AsyncBaseManager(verbose=False) as manager:
        manager.redis_client = fake

        # Creamos un rate limiter: 5 peticiones por ventana de 10 segundos
        limiter = RateLimiter(manager, max_requests=5, window_seconds=10)

        print("=== Rate Limiter - 5 peticiones / 10 segundos ===\n")

        # Simulamos 8 peticiones de un cliente
        client_id = "usuario_123"
        for i in range(8):
            permitido, info = await limiter.is_allowed(client_id)
            estado = "PERMITIDA" if permitido else "DENEGADA"
            print(
                f"  Petición {i + 1}: {estado} | "
                f"Usadas: {info['peticiones_usadas']}/{5} | "
                f"Restantes: {info['peticiones_restantes']}"
            )

        # Verificamos las entradas en Redis
        print("\n=== Estado en Redis ===")
        key = f"ratelimit:{client_id}"
        entradas = await manager._execute("zrange", key, 0, -1, "WITHSCORES")
        print(f"  Entradas en sorted set: {len(entradas) // 2}")
        ttl = await manager._execute("ttl", key)
        print(f"  TTL restante: {ttl}s")

        # Probamos con otro cliente (debería tener su propio límite)
        print("\n=== Otro cliente (límite independiente) ===")
        client_id_2 = "usuario_456"
        permitido, info = await limiter.is_allowed(client_id_2)
        estado = "PERMITIDA" if permitido else "DENEGADA"
        print(f"  Petición 1 de usuario_456: {estado}")

    await fake.aclose()
    print("\nRate Limiter completado")


if __name__ == "__main__":
    asyncio.run(main())
