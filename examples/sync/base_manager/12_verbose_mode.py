"""Ejemplo 12: Modo verbose y su impacto en el logging.

Demuestra la diferencia entre ejecutar BaseManager con verbose=True
y verbose=False, y cómo afecta al registro de operaciones.
"""

import fakeredis

from wredis._base import BaseManager

print("=== Modo Verbose vs Silencioso ===\n")

# Escenario 1: Manager con verbose=True
print("--- Escenario 1: verbose=True ---")
manager_verbose = BaseManager(verbose=True)
manager_verbose.redis_client = fakeredis.FakeRedis(decode_responses=True)

print(f"Estado verbose: {manager_verbose.verbose}")
manager_verbose.log("Operación iniciada", level="info")
manager_verbose._execute("set", "verbose:clave", "datos_prueba")
manager_verbose.log("Datos almacenados", level="info")
valor = manager_verbose._execute("get", "verbose:clave")
print(f"Valor recuperado: {valor}")

# Escenario 2: Manager con verbose=False
print("\n--- Escenario 2: verbose=False ---")
manager_silencioso = BaseManager(verbose=False)
manager_silencioso.redis_client = fakeredis.FakeRedis(decode_responses=True)

print(f"Estado verbose: {manager_silencioso.verbose}")
manager_silencioso.log("Esta operación NO se registra", level="info")
manager_silencioso._execute("set", "silencioso:clave", "datos_prueba")
manager_silencioso.log("Datos almacenados (sin registro)", level="info")
valor = manager_silencioso._execute("get", "silencioso:clave")
print(f"Valor recuperado: {valor}")
print("(Los mensajes de log anteriores NO aparecieron)")

# Escenario 3: Cambio dinámico del modo verbose
print("\n--- Escenario 3: Cambio dinámico de verbose ---")
manager_dinamico = BaseManager(verbose=False)
manager_dinamico.redis_client = fakeredis.FakeRedis(decode_responses=True)

print(f"Verbose inicial: {manager_dinamico.verbose}")
manager_dinamico.log("Mensaje 1 (no aparece)", level="info")

# Cambiamos a verbose=True
manager_dinamico.verbose = True
print(f"Verbose después de cambiar: {manager_dinamico.verbose}")
manager_dinamico.log("Mensaje 2 (sí aparece)", level="info")

# Volvemos a verbose=False
manager_dinamico.verbose = False
print(f"Verbose después de segundo cambio: {manager_dinamico.verbose}")
manager_dinamico.log("Mensaje 3 (no aparece)", level="info")

manager_verbose.close()
manager_silencioso.close()
manager_dinamico.close()
print("\nTodas las conexiones cerradas correctamente")
