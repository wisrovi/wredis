"""11 - Múltiples bases de datos

Este ejemplo demuestra cómo conectar y operar sobre múltiples
bases de datos de Redis (db=0, db=1, db=2) usando instancias
separadas de AsyncBaseManager.
"""

import asyncio

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager


async def main():
    # Creamos un FakeRedis compartido para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    # Creamos managers para diferentes bases de datos
    # Nota: fakeredis comparte el mismo estado, pero usamos prefijos para simular aislamiento
    db_cache = AsyncBaseManager(decode_responses=True, verbose=False)
    db_sesiones = AsyncBaseManager(decode_responses=True, verbose=False)
    db_temporal = AsyncBaseManager(decode_responses=True, verbose=False)

    # Inyectamos el mismo FakeRedis en todos
    db_cache.redis_client = fake
    db_sesiones.redis_client = fake
    db_temporal.redis_client = fake

    try:
        # Verificamos todas las conexiones
        print("=== Verificando conexiones ===")
        for nombre, mgr in [
            ("Cache (db=0)", db_cache),
            ("Sesiones (db=1)", db_sesiones),
            ("Temporal (db=2)", db_temporal),
        ]:
            estado = await mgr.health_check()
            print(f"  {nombre}: {estado}")

        # Escribimos datos en cada base de datos (usando prefijos para simular aislamiento)
        print("\n=== Escribiendo en db=0 (Cache) ===")
        await db_cache._execute("set", "db0:cache:pagina:inicio", "<html>...</html>")
        await db_cache._execute("set", "db0:cache:pagina:about", "<html>about</html>")
        valor = await db_cache._execute("get", "db0:cache:pagina:inicio")
        print(f"  cache:pagina:inicio = {valor}")

        print("\n=== Escribiendo en db=1 (Sesiones) ===")
        await db_sesiones._execute("set", "db1:sesion:abc123", '{"user": "admin"}')
        await db_sesiones._execute("set", "db1:sesion:def456", '{"user": "editor"}')
        valor = await db_sesiones._execute("get", "db1:sesion:abc123")
        print(f"  sesion:abc123 = {valor}")

        print("\n=== Escribiendo en db=2 (Temporal) ===")
        await db_temporal._execute("set", "db2:temp:job:001", "procesando", ex=60)
        await db_temporal._execute("set", "db2:temp:job:002", "pendiente", ex=120)
        valor = await db_temporal._execute("get", "db2:temp:job:001")
        ttl = await db_temporal._execute("ttl", "db2:temp:job:001")
        print(f"  temp:job:001 = {valor} (TTL: {ttl}s)")

        # Verificamos aislamiento entre bases de datos (simulado con prefijos)
        print("\n=== Verificando aislamiento ===")
        dato_en_db0 = await db_cache._execute("get", "db1:sesion:abc123")
        dato_en_db1 = await db_sesiones._execute("get", "db0:cache:pagina:inicio")
        print(f"  sesion:abc123 en db=0: {dato_en_db0} (debe ser None)")
        print(f"  cache:pagina:inicio en db=1: {dato_en_db1} (debe ser None)")

    finally:
        # Cerramos todas las conexiones
        await db_cache.close()
        await db_sesiones.close()
        await db_temporal.close()
        await fake.aclose()
        print("\nTodas las conexiones cerradas")


if __name__ == "__main__":
    asyncio.run(main())
