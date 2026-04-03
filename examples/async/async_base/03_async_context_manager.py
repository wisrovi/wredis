"""03 - Uso del contexto asíncrono (async with)

Este ejemplo muestra cómo usar AsyncBaseManager como un gestor
de contexto asíncrono con 'async with', lo que garantiza que
la conexión se cierre automáticamente al salir del bloque.
"""

import asyncio

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager


async def main():
    # Creamos un FakeRedis para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    # Usamos 'async with' para gestión automática del ciclo de vida
    # La conexión se abre al entrar y se cierra al salir del bloque
    async with AsyncBaseManager(verbose=True) as manager:
        # Inyectamos el FakeRedis
        manager.redis_client = fake

        # Verificamos la conexión dentro del contexto
        conectado = await manager.health_check()
        print(f"Dentro del contexto - Conectado: {conectado}")

        # Realizamos varias operaciones de forma segura
        await manager._execute("set", "clave1", "valor1")
        await manager._execute("set", "clave2", "valor2")

        valor1 = await manager._execute("get", "clave1")
        valor2 = await manager._execute("get", "clave2")
        print(f"clave1 = {valor1}, clave2 = {valor2}")

    # Fuera del contexto, la conexión ya está cerrada
    await fake.aclose()
    print("Fuera del contexto - conexión cerrada automáticamente")


if __name__ == "__main__":
    asyncio.run(main())
