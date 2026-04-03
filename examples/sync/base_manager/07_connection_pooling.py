"""Ejemplo 07: Gestión del pool de conexiones.

Demuestra cómo BaseManager maneja internamente un pool de conexiones
y cómo se puede configurar el número máximo de conexiones.
"""

import redis

import fakeredis

from wredis._base import BaseManager

print("=== Gestión del Pool de Conexiones ===\n")

# Creamos un manager con un pool de conexiones configurado
manager = BaseManager(
    max_connections=5,
    decode_responses=True,
    verbose=False,
)

# Reemplazamos con FakeRedis pero mantenemos el pool original
print(f"Pool de conexiones creado: {type(manager._pool).__name__}")
print(f"Máximo de conexiones configurado: {manager._pool.max_connections}")

# Configuramos FakeRedis para las pruebas
manager.redis_client = fakeredis.FakeRedis(decode_responses=True)

# Verificamos que las operaciones funcionan con el pool
print("\nEjecutando operaciones con el pool de conexiones:")

# Múltiples operaciones que usarían el pool en un entorno real
for i in range(3):
    manager._execute("set", f"pool:clave:{i}", f"valor_{i}")
    valor = manager._execute("get", f"pool:clave:{i}")
    print(f"  Operación {i + 1}: SET/GET de pool:clave:{i} = {valor}")

# Información del pool
print(f"\nEstado del pool:")
print(f"  Tipo de pool: {type(manager._pool).__name__}")
print(f"  Conexiones máximas: {manager._pool.max_connections}")

# Cerramos el pool explícitamente
manager.close()
print("\nPool de conexiones cerrado correctamente")
