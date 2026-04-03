"""05 - Integración con FastAPI

Este ejemplo muestra cómo integrar AsyncBaseManager con FastAPI
para crear endpoints que interactúan con Redis de forma asíncrona.
Se usa una startup/shutdown lifecycle para gestionar la conexión.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager

# Variable global para el manager de Redis
redis_manager: AsyncBaseManager | None = None


@asynccontextmanager
async def lifespan(app: Dict[str, Any]):
    """Gestiona el ciclo de vida de la aplicación FastAPI."""
    global redis_manager
    # Creamos un FakeRedis para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    # Al iniciar: creamos la conexión
    redis_manager = AsyncBaseManager(verbose=False)
    redis_manager.redis_client = fake
    conectado = await redis_manager.health_check()
    print(f"FastAPI startup - Redis conectado: {conectado}")
    yield
    # Al cerrar: liberamos la conexión
    if redis_manager:
        await redis_manager.close()
        await fake.aclose()
        print("FastAPI shutdown - Redis desconectado")


# Simulación de la app FastAPI sin necesidad del framework instalado
async def simulate_fastapi():
    """Simula el comportamiento de FastAPI para demostración."""
    global redis_manager

    app = {"name": "mi_api"}

    # Simulamos el startup
    async with lifespan(app):
        # Endpoint GET /health
        print("\n--- GET /health ---")
        estado = await redis_manager.health_check()  # type: ignore[union-attr]
        print(f'{{"status": "healthy", "redis": {estado}}}')

        # Endpoint POST /cache
        print("\n--- POST /cache ---")
        await redis_manager._execute("set", "cache:página:inicio", "contenido HTML")  # type: ignore[union-attr]
        print('{"action": "cached", "key": "cache:página:inicio"}')

        # Endpoint GET /cache/{key}
        print("\n--- GET /cache/cache:página:inicio ---")
        contenido = await redis_manager._execute("get", "cache:página:inicio")  # type: ignore[union-attr]
        print(f'{{"key": "cache:página:inicio", "value": "{contenido}"}}')

        # Endpoint DELETE /cache/{key}
        print("\n--- DELETE /cache/cache:página:inicio ---")
        await redis_manager._execute("delete", "cache:página:inicio")  # type: ignore[union-attr]
        print('{"action": "deleted", "key": "cache:página:inicio"}')

    print("\nFastAPI simulado completado")


async def main():
    await simulate_fastapi()


if __name__ == "__main__":
    asyncio.run(main())
