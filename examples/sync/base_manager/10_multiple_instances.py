"""Ejemplo 10: Múltiples instancias de BaseManager.

Demuestra cómo crear y gestionar múltiples instancias independientes
de BaseManager conectadas a diferentes bases de datos.
"""

import fakeredis

from wredis._base import BaseManager

print("=== Múltiples Instancias de BaseManager ===\n")

# Creamos tres instancias independientes para diferentes propósitos
# Cada una apunta a una base de datos diferente
manager_sesion = BaseManager(db=0, verbose=False)
manager_cache = BaseManager(db=1, verbose=False)
manager_colas = BaseManager(db=2, verbose=False)

# Reemplazamos cada una con su propio FakeRedis
manager_sesion.redis_client = fakeredis.FakeRedis(decode_responses=True)
manager_cache.redis_client = fakeredis.FakeRedis(decode_responses=True)
manager_colas.redis_client = fakeredis.FakeRedis(decode_responses=True)

print("Instancias creadas:")
print(f"  Sesiones (db=0): {type(manager_sesion.redis_client).__name__}")
print(f"  Caché (db=1): {type(manager_cache.redis_client).__name__}")
print(f"  Colas (db=2): {type(manager_colas.redis_client).__name__}")

# Operaciones independientes en cada instancia
print("\nOperaciones en cada instancia:")

# Instancia de sesiones
manager_sesion._execute("set", "sesion:usuario:1", "token_abc123")
sesion = manager_sesion._execute("get", "sesion:usuario:1")
print(f"  Sesión - usuario:1 = {sesion}")

# Instancia de caché
manager_cache._execute("set", "cache:página:inicio", "<html>contenido</html>")
cache = manager_cache._execute("get", "cache:página:inicio")
print(f"  Caché - página:inicio = {cache[:30]}...")

# Instancia de colas
manager_colas._execute("lpush", "cola:tareas", "enviar_email")
manager_colas._execute("lpush", "cola:tareas", "generar_reporte")
tarea = manager_colas._execute("rpop", "cola:tareas")
print(f"  Colas - tarea procesada = {tarea}")

# Verificamos que las instancias son independientes
print("\nVerificando independencia:")
print(f"  Sesiones puede ver datos de caché: {manager_sesion._execute('get', 'cache:página:inicio')}")
print(f"  (Las instancias de FakeRedis son independientes)")

# Cerramos todas las instancias
manager_sesion.close()
manager_cache.close()
manager_colas.close()
print("\nTodas las instancias cerradas correctamente")
