"""12 - Patrón Worker/Producer asíncrono

Este ejemplo implementa un patrón productor-consumidor usando
Redis como cola de mensajes, con AsyncBaseManager para gestionar
las operaciones de enqueue y dequeue asíncronas.
"""

import asyncio

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager

COLA_TRABAJO = "cola:trabajos"
COLA_RESULTADOS = "cola:resultados"


async def productor(manager: AsyncBaseManager, num_trabajos: int):
    """Produce trabajos y los encola en Redis."""
    for i in range(num_trabajos):
        trabajo = f"trabajo_{i}:datos_{i * 10}"
        await manager._execute("rpush", COLA_TRABAJO, trabajo)
        print(f"  [Productor] Encolado: {trabajo}")
        await asyncio.sleep(0.05)  # Simula tiempo entre producciones
    print(f"  [Productor] {num_trabajos} trabajos producidos")


async def consumidor(manager: AsyncBaseManager):
    """Consume trabajos de la cola y procesa resultados."""
    procesados = 0
    while True:
        # LPOP devuelve None si la cola está vacía
        trabajo = await manager._execute("lpop", COLA_TRABAJO)
        if trabajo is None:
            break

        # Simulamos procesamiento
        resultado = f"resultado_de_{trabajo}"
        await manager._execute("rpush", COLA_RESULTADOS, resultado)
        print(f"  [Consumidor] Procesado: {trabajo} -> {resultado}")
        procesados += 1
        await asyncio.sleep(0.02)

    print(f"  [Consumidor] {procesados} trabajos procesados")
    return procesados


async def main():
    # Creamos un FakeRedis para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async with AsyncBaseManager(verbose=False) as manager:
        manager.redis_client = fake

        # Limpiamos colas previas
        await manager._execute("delete", COLA_TRABAJO, COLA_RESULTADOS)

        print("=== Iniciando patrón Producer/Consumer ===")

        # Ejecutamos productor y consumidor secuencialmente para claridad
        print("\n--- Producción ---")
        await productor(manager, 5)

        print("\n--- Consumo ---")
        total = await consumidor(manager)

        # Verificamos resultados
        print("\n=== Verificación ===")
        longitud = await manager._execute("llen", COLA_RESULTADOS)
        print(f"  Resultados en cola: {longitud}")

        # Leemos todos los resultados
        resultados = await manager._execute("lrange", COLA_RESULTADOS, 0, -1)
        print(f"  Todos los resultados: {resultados}")

    await fake.aclose()
    print(f"\nPatrón Worker/Consumer completado: {total} trabajos procesados")


if __name__ == "__main__":
    asyncio.run(main())
