"""Ejemplo 11: Operaciones por lotes (batch) con _execute.

Demuestra cómo ejecutar múltiples operaciones de Redis de forma
eficiente usando el método _execute con reintentos automáticos.
"""

import fakeredis

from wredis._base import BaseManager

print("=== Operaciones por Lotes (Batch) ===\n")

with BaseManager(verbose=False) as manager:
    manager.redis_client = fakeredis.FakeRedis(decode_responses=True)

    # Lote 1: Inserción masiva de datos
    print("1. Inserción masiva de datos:")
    datos = {
        "batch:producto:1": '{"nombre": "Laptop", "precio": 999.99}',
        "batch:producto:2": '{"nombre": "Mouse", "precio": 29.99}',
        "batch:producto:3": '{"nombre": "Teclado", "precio": 79.99}',
        "batch:producto:4": '{"nombre": "Monitor", "precio": 349.99}',
        "batch:producto:5": '{"nombre": "Webcam", "precio": 59.99}',
    }

    for clave, valor in datos.items():
        manager._execute("set", clave, valor)
    print(f"   {len(datos)} productos insertados")

    # Lote 2: Lectura masiva
    print("\n2. Lectura masiva de datos:")
    for clave in datos.keys():
        valor = manager._execute("get", clave)
        nombre = valor.split('"nombre": "')[1].split('"')[0] if valor else "N/A"
        print(f"   {clave}: {nombre}")

    # Lote 3: Operaciones con listas
    print("\n3. Operaciones con listas:")
    tareas = ["procesar_pedido", "enviar_notificacion", "actualizar_inventario", "generar_factura"]
    for tarea in tareas:
        manager._execute("lpush", "batch:cola:procesamiento", tarea)
    print(f"   {len(tareas)} tareas encoladas")

    longitud = manager._execute("llen", "batch:cola:procesamiento")
    print(f"   Longitud de la cola: {longitud}")

    # Lote 4: Operaciones con hashes
    print("\n4. Operaciones con hashes:")
    manager._execute(
        "hset",
        "batch:config:app",
        mapping={
            "version": "2.5.0",
            "entorno": "produccion",
            "debug": "false",
            "max_usuarios": "1000",
        },
    )
    config = manager._execute("hgetall", "batch:config:app")
    print(f"   Configuración: {config}")

    # Lote 5: Operaciones con conjuntos
    print("\n5. Operaciones con conjuntos:")
    for usuario in ["ana", "carlos", "maria", "pedro", "ana"]:
        manager._execute("sadd", "batch:usuarios:activos", usuario)
    total = manager._execute("scard", "batch:usuarios:activos")
    print(f"   Usuarios activos únicos: {total}")

print("\nTodas las operaciones por lotes completadas")
