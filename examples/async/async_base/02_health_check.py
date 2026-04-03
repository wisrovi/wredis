"""02 - Verificación de salud (health check)

Este ejemplo demuestra el uso del método health_check() para
verificar que la conexión a Redis está activa y funcionando
correctamente, incluyendo el manejo de errores.
"""

import asyncio

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager
from wredis._exceptions import OperationError


async def main():
    # Creamos un FakeRedis para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    # Creamos el manager con verbose activado para ver los logs
    manager = AsyncBaseManager(verbose=True)
    manager.redis_client = fake

    # Realizamos el health check - devuelve True si Redis responde
    try:
        estado = await manager.health_check()
        print(f"Estado de la conexión: {estado}")
    except OperationError as e:
        print(f"Error en health check: {e}")

    # El health check también se puede usar antes de operaciones críticas
    if await manager.health_check():
        print("Conexión verificada, procediendo con operaciones")
        await manager._execute("set", "estado", "operativo")
        valor = await manager._execute("get", "estado")
        print(f"Valor almacenado: {valor}")
    else:
        print("Conexión no disponible")

    await manager.close()
    await fake.aclose()
    print("Conexión cerrada")


if __name__ == "__main__":
    asyncio.run(main())
