"""Ejemplo 05: Ejecución de operaciones con reintentos automáticos.

Demuestra el método _execute() que ejecuta operaciones de Redis
con lógica de reintentos (retry) usando backoff exponencial.
"""

import fakeredis

from wredis._base import BaseManager

print("=== Ejecución con Reintentos (_execute) ===\n")

# Creamos el manager con FakeRedis
with BaseManager(verbose=False) as manager:
    manager.redis_client = fakeredis.FakeRedis(decode_responses=True)

    # _execute permite ejecutar cualquier operación del cliente Redis
    # con reintentos automáticos en caso de fallos de conexión
    print("Ejecutando operaciones con _execute():")

    # Operación SET con reintentos
    resultado_set = manager._execute("set", "retry:clave", "valor_con_reintento")
    print(f"  SET ejecutado: {resultado_set}")

    # Operación GET con reintentos
    resultado_get = manager._execute("get", "retry:clave")
    print(f"  GET ejecutado: {resultado_get}")

    # Operación INCR con reintentos
    manager._execute("set", "retry:contador", "0")
    resultado_incr = manager._execute("incr", "retry:contador")
    print(f"  INCR ejecutado: {resultado_incr}")

    # Operación HSET con reintentos
    resultado_hset = manager._execute("hset", "retry:hash", mapping={"campo1": "valor1", "campo2": "valor2"})
    print(f"  HSET ejecutado: {resultado_hset} campos")

    # Operación HGETALL con reintentos
    resultado_hgetall = manager._execute("hgetall", "retry:hash")
    print(f"  HGETALL ejecutado: {resultado_hgetall}")

print("\nTodas las operaciones se ejecutaron con reintentos automáticos")
