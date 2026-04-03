"""06 - Operaciones concurrentes

Este ejemplo demuestra cómo ejecutar múltiples operaciones de Redis
de forma concurrente usando asyncio.gather() para maximizar el
rendimiento en operaciones independientes.
"""

import asyncio

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager


async def escribir_dato(manager: AsyncBaseManager, clave: str, valor: str):
    """Escribe un dato en Redis de forma asíncrona."""
    await manager._execute("set", clave, valor)
    return f"Escrito: {clave}={valor}"


async def leer_dato(manager: AsyncBaseManager, clave: str):
    """Lee un dato de Redis de forma asíncrona."""
    valor = await manager._execute("get", clave)
    return f"Leído: {clave}={valor}"


async def main():
    # Creamos un FakeRedis para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async with AsyncBaseManager(verbose=False) as manager:
        manager.redis_client = fake

        # Escritura concurrente de múltiples claves
        print("=== Escritura concurrente ===")
        tareas_escritura = [escribir_dato(manager, f"usuario:{i}", f"nombre_{i}") for i in range(1, 6)]
        resultados = await asyncio.gather(*tareas_escritura)
        for r in resultados:
            print(f"  {r}")

        # Lectura concurrente de múltiples claves
        print("\n=== Lectura concurrente ===")
        tareas_lectura = [leer_dato(manager, f"usuario:{i}") for i in range(1, 6)]
        resultados = await asyncio.gather(*tareas_lectura)
        for r in resultados:
            print(f"  {r}")

        # Operaciones mixtas concurrentes
        print("\n=== Operaciones mixtas concurrentes ===")
        mixtas = [
            manager._execute("set", "temporal", "dato"),
            manager._execute("get", "usuario:1"),
            manager._execute("exists", "usuario:3"),
            manager._execute("ttl", "usuario:5"),
        ]
        resultados_mixtos = await asyncio.gather(*mixtas)
        print(f"  SET temporal: {resultados_mixtos[0]}")
        print(f"  GET usuario:1: {resultados_mixtos[1]}")
        print(f"  EXISTS usuario:3: {bool(resultados_mixtos[2])}")
        print(f"  TTL usuario:5: {resultados_mixtos[3]}")

    await fake.aclose()
    print("\nOperaciones concurrentes completadas")


if __name__ == "__main__":
    asyncio.run(main())
