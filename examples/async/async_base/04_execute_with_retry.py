"""04 - Ejecución con reintentos (_execute)

Este ejemplo demuestra el método _execute() que ejecuta operaciones
de Redis con lógica de reintento exponencial (hasta 3 intentos)
ante fallos de conexión.
"""

import asyncio

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager


async def main():
    # Creamos un FakeRedis para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async with AsyncBaseManager(verbose=True) as manager:
        # Inyectamos el FakeRedis
        manager.redis_client = fake

        # _execute reintentará automáticamente hasta 3 veces con backoff exponencial
        # Los delays son: 0.1s, 0.2s antes de cada reintento

        # Operación SET con reintento automático
        resultado_set = await manager._execute("set", "usuario:1:nombre", "Ana")
        print(f"SET usuario:1:nombre = {resultado_set}")

        # Operación GET con reintento automático
        nombre = await manager._execute("get", "usuario:1:nombre")
        print(f"GET usuario:1:nombre = {nombre}")

        # Operaciones con expiración
        await manager._execute("set", "token:abc123", "secreto", ex=300)
        ttl = await manager._execute("ttl", "token:abc123")
        print(f"TTL del token: {ttl} segundos")

        # Verificar existencia
        existe = await manager._execute("exists", "usuario:1:nombre")
        print(f"¿Existe usuario:1:nombre? {bool(existe)}")

        # Eliminar clave
        eliminado = await manager._execute("delete", "usuario:1:nombre")
        print(f"Claves eliminadas: {eliminado}")

    await fake.aclose()
    print("Operaciones con reintento completadas")


if __name__ == "__main__":
    asyncio.run(main())
