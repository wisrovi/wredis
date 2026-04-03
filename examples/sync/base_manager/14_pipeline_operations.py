"""Ejemplo 14: Pipeline de operaciones con BaseManager.

Demuestra cómo usar pipelines de Redis junto con BaseManager para
ejecutar múltiples operaciones de forma atómica y eficiente.
"""

import fakeredis

from wredis._base import BaseManager

print("=== Pipeline de Operaciones ===\n")

with BaseManager(verbose=False) as manager:
    manager.redis_client = fakeredis.FakeRedis(decode_responses=True)

    # Pipeline 1: Operaciones de escritura masiva
    print("1. Pipeline de escritura masiva:")
    pipe = manager.redis_client.pipeline()
    for i in range(5):
        pipe.set(f"pipeline:clave:{i}", f"valor_{i}")
    resultados = pipe.execute()
    print(f"   {len(resultados)} operaciones SET ejecutadas en pipeline")
    print(f"   Resultados: {resultados}")

    # Verificamos que los datos se almacenaron
    for i in range(5):
        valor = manager._execute("get", f"pipeline:clave:{i}")
        print(f"   pipeline:clave:{i} = {valor}")

    # Pipeline 2: Operaciones mixtas
    print("\n2. Pipeline de operaciones mixtas:")
    pipe = manager.redis_client.pipeline()
    pipe.set("pipeline:usuario:nombre", "Ana García")
    pipe.set("pipeline:usuario:email", "ana@ejemplo.com")
    pipe.set("pipeline:usuario:rol", "administrador")
    pipe.incr("pipeline:contador:usuarios")
    resultados = pipe.execute()
    print(f"   {len(resultados)} operaciones mixtas ejecutadas")

    # Verificamos los datos
    nombre = manager._execute("get", "pipeline:usuario:nombre")
    email = manager._execute("get", "pipeline:usuario:email")
    rol = manager._execute("get", "pipeline:usuario:rol")
    contador = manager._execute("get", "pipeline:contador:usuarios")
    print(f"   Nombre: {nombre}")
    print(f"   Email: {email}")
    print(f"   Rol: {rol}")
    print(f"   Contador de usuarios: {contador}")

    # Pipeline 3: Operaciones de lectura
    print("\n3. Pipeline de lectura:")
    pipe = manager.redis_client.pipeline()
    for i in range(5):
        pipe.get(f"pipeline:clave:{i}")
    resultados = pipe.execute()
    print(f"   {len(resultados)} valores leídos en pipeline")
    print(f"   Valores: {resultados}")

    # Pipeline 4: Operaciones con hashes
    print("\n4. Pipeline con hashes:")
    pipe = manager.redis_client.pipeline()
    pipe.hset("pipeline:producto:1", mapping={"nombre": "Laptop", "precio": "999.99"})
    pipe.hset("pipeline:producto:2", mapping={"nombre": "Mouse", "precio": "29.99"})
    pipe.hgetall("pipeline:producto:1")
    pipe.hgetall("pipeline:producto:2")
    resultados = pipe.execute()
    print(f"   {len(resultados)} operaciones con hashes")
    print(f"   Producto 1: {resultados[2]}")
    print(f"   Producto 2: {resultados[3]}")

print("\nTodos los pipelines ejecutados correctamente")
