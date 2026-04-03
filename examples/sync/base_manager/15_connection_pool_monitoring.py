"""Ejemplo 15: Monitoreo del pool de conexiones.

Demuestra cómo monitorear y obtener información del estado del pool
de conexiones de Redis gestionado por BaseManager.
"""

import fakeredis

from wredis._base import BaseManager

print("=== Monitoreo del Pool de Conexiones ===\n")

# Creamos un manager con configuración específica para monitoreo
manager = BaseManager(
    max_connections=10,
    socket_timeout=5.0,
    verbose=False,
)

# Reemplazamos con FakeRedis para las pruebas
manager.redis_client = fakeredis.FakeRedis(decode_responses=True)

# Información del pool
print("1. Información del pool:")
print(f"   Tipo: {type(manager._pool).__name__}")
print(f"   Máximo de conexiones: {manager._pool.max_connections}")
print(f"   Host configurado: {manager._pool.connection_kwargs.get('host', 'localhost')}")
print(f"   Puerto configurado: {manager._pool.connection_kwargs.get('port', 6379)}")
print(f"   Base de datos: {manager._pool.connection_kwargs.get('db', 0)}")
print(f"   Timeout: {manager._pool.connection_kwargs.get('socket_timeout', 5.0)}s")

# Realizamos operaciones y monitoreamos
print("\n2. Monitoreo durante operaciones:")
for i in range(3):
    manager._execute("set", f"monitor:clave:{i}", f"valor_{i}")
    valor = manager._execute("get", f"monitor:clave:{i}")
    print(f"   Operación {i + 1}: {valor}")

# Estado después de las operaciones
print("\n3. Estado del pool después de operaciones:")
print(f"   Conexiones máximas: {manager._pool.max_connections}")

# Información del cliente
print("\n4. Información del cliente Redis:")
print(f"   Tipo de cliente: {type(manager.redis_client).__name__}")
print(
    f"   Decodificar respuestas: {manager.redis_client.connection_pool.connection_kwargs.get('decode_responses', False)}"
)

# Verificación de salud
print("\n5. Verificación de salud:")
estado = manager.health_check()
print(f"   Estado: {'ACTIVO' if estado else 'INACTIVO'}")

# Simulamos monitoreo de métricas
print("\n6. Métricas simuladas:")
metricas = {
    "conexiones_maximas": manager._pool.max_connections,
    "estado_conexion": "activo" if manager.health_check() else "inactivo",
    "timeout_socket": f"{manager._pool.connection_kwargs.get('socket_timeout', 5.0)}s",
    "operaciones_exitosas": 6,
    "operaciones_fallidas": 0,
}
for metrica, valor in metricas.items():
    print(f"   {metrica}: {valor}")

# Cerramos y verificamos
manager.close()
print("\n7. Después del cierre:")
print("   Pool desconectado correctamente")
print("   Monitoreo completado")
