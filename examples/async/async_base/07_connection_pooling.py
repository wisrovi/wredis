"""07 - Configuración del pool de conexiones

Este ejemplo muestra cómo configurar el pool de conexiones de Redis
con parámetros personalizados como max_connections, socket_timeout
y decode_responses para optimizar el rendimiento.
"""

import asyncio

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager


async def main():
    # Creamos un FakeRedis para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    # Configuramos un pool de conexiones con parámetros personalizados
    manager = AsyncBaseManager(
        decode_responses=True,  # Las respuestas se devuelven como str en vez de bytes
        socket_timeout=10.0,  # Timeout de 10 segundos para operaciones lentas
        max_connections=20,  # Pool de hasta 20 conexiones simultáneas
        verbose=True,
    )
    # Inyectamos el FakeRedis
    manager.redis_client = fake

    # Verificamos la conexión
    conectado = await manager.health_check()
    print(f"Conexión establecida: {conectado}")

    # El pool de conexiones permite reutilizar conexiones existentes
    # Esto es más eficiente que crear una nueva conexión por operación
    for i in range(5):
        await manager._execute("set", f"pool:clave:{i}", f"valor_{i}")
        print(f"  Set pool:clave:{i} -> valor_{i}")

    # Leemos todas las claves usando el mismo pool
    print("\nLeyendo claves del pool:")
    for i in range(5):
        valor = await manager._execute("get", f"pool:clave:{i}")
        print(f"  pool:clave:{i} = {valor}")

    # Mostramos información del pool
    print(f"\nTamaño máximo del pool: 20 conexiones")
    print(f"Timeout del socket: 10.0 segundos")
    print(f"Decode responses: True")

    await manager.close()
    await fake.aclose()
    print("\nPool de conexiones cerrado")


if __name__ == "__main__":
    asyncio.run(main())
