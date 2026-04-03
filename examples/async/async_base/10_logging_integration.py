"""10 - Sistema de logging integrado

Este ejemplo muestra el uso del método log() de AsyncBaseManager
para registrar mensajes con diferentes niveles de severidad
integrados con loguru.
"""

import asyncio

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager


async def main():
    # Creamos un FakeRedis para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async with AsyncBaseManager(verbose=True) as manager:
        manager.redis_client = fake

        # Verificamos conexión
        conectado = await manager.health_check()
        print(f"Conexión establecida: {conectado}")

        # Usamos el sistema de logging integrado
        print("\n=== Mensajes de log ===")
        manager.log("Aplicación iniciada correctamente", "info")
        manager.log("Procesando datos de usuario", "debug")
        manager.log("Advertencia: cache casi lleno", "warning")

        # Realizamos operaciones con logging
        print("\n=== Operaciones con logging ===")
        await manager._execute("set", "app:estado", "ejecutando")
        manager.log("Estado de la aplicación actualizado", "info")

        estado = await manager._execute("get", "app:estado")
        print(f"Estado actual: {estado}")

        # Simulamos un escenario de error
        manager.log("Intentando operación crítica...", "info")
        try:
            await manager._execute("set", "app:datos", '{"items": [1, 2, 3]}')
            manager.log("Datos críticos guardados exitosamente", "info")
        except Exception as e:
            manager.log(f"Error al guardar datos: {e}", "error")

        # Log de finalización
        manager.log("Proceso completado sin errores", "info")

    await fake.aclose()
    print("\nSistema de logging completado")


if __name__ == "__main__":
    asyncio.run(main())
