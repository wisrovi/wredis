"""01 - Inicialización básica de AsyncBaseManager

Este ejemplo muestra cómo crear una instancia de AsyncBaseManager
con los parámetros por defecto y verificar la conexión usando
fakeredis.aioredis como backend de prueba.
"""

import asyncio

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager


async def main():
    # Creamos un FakeRedis para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    # Creamos un manager con configuración por defecto
    # Inyectamos el cliente FakeRedis para evitar conexión real
    manager = AsyncBaseManager(verbose=True)
    manager.redis_client = fake

    # Verificamos que la conexión esté activa
    is_alive = await manager.health_check()
    print(f"Redis conectado: {is_alive}")

    # Realizamos una operación simple para confirmar
    resultado = await manager._execute("set", "saludo", "hola mundo")
    print(f"Resultado de SET: {resultado}")

    valor = await manager._execute("get", "saludo")
    print(f"Resultado de GET: {valor}")

    # Cerramos la conexión al finalizar
    await manager.close()
    await fake.aclose()
    print("Conexión cerrada correctamente")


if __name__ == "__main__":
    asyncio.run(main())
