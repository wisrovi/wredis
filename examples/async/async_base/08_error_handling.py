"""08 - Manejo de errores

Este ejemplo demuestra las estrategias de manejo de errores al usar
AsyncBaseManager, incluyendo capturas de OperationError, reintentos
automáticos y graceful degradation.
"""

import asyncio

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager
from wredis._exceptions import OperationError


async def main():
    # Creamos un FakeRedis para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async with AsyncBaseManager(verbose=True) as manager:
        manager.redis_client = fake

        # 1. Manejo de error en health check
        print("=== 1. Health check con try/except ===")
        try:
            estado = await manager.health_check()
            print(f"  Health check exitoso: {estado}")
        except OperationError as e:
            print(f"  Error de conexión: {e}")

        # 2. Manejo de error en operaciones
        print("\n=== 2. Operación con try/except ===")
        try:
            # Operación válida
            await manager._execute("set", "datos:seguros", "valor_valido")
            resultado = await manager._execute("get", "datos:seguros")
            print(f"  Operación exitosa: {resultado}")
        except OperationError as e:
            print(f"  Error en operación: {e}")

        # 3. Operación con argumentos inválidos
        print("\n=== 3. Operación con argumentos inválidos ===")
        try:
            # Esto fallará porque 'get' no acepta múltiples argumentos posicionales
            await manager._execute("get", "clave1", "clave2")
        except (OperationError, Exception) as e:
            print(f"  Error capturado: {type(e).__name__}: {e}")

        # 4. Graceful degradation - fallback cuando Redis falla
        print("\n=== 4. Graceful degradation ===")
        cache_key = "config:app"
        try:
            valor_cache = await manager._execute("get", cache_key)
            if valor_cache:
                config = valor_cache
            else:
                # Simulamos carga desde base de datos
                config = "configuracion_por_defecto"
                await manager._execute("set", cache_key, config, ex=60)
            print(f"  Configuración obtenida: {config}")
        except OperationError:
            # Fallback si Redis no está disponible
            config = "configuracion_de_respaldo"
            print(f"  Usando fallback: {config}")

        # 5. Reintento automático (ya integrado en _execute)
        print("\n=== 5. Reintento automático ===")
        print("  _execute reintenta automáticamente hasta 3 veces")
        print("  con backoff exponencial: 0.1s, 0.2s")
        await manager._execute("set", "reintento:clave", "valor_seguro")
        print(f"  Operación completada con reintentos habilitados")

    await fake.aclose()
    print("\nManejo de errores completado")


if __name__ == "__main__":
    asyncio.run(main())
