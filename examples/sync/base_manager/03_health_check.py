"""Ejemplo 03: Verificación de salud (health check).

Demuestra el uso del método health_check() para verificar que la
conexión con Redis está activa y funcionando correctamente.
"""

import fakeredis

from wredis._base import BaseManager

# Creamos el manager y configuramos FakeRedis
manager = BaseManager(verbose=False)
manager.redis_client = fakeredis.FakeRedis(decode_responses=True)

# Verificamos el estado de la conexión
print("=== Verificación de Salud (Health Check) ===\n")

# health_check() devuelve True si la conexión está activa
estado = manager.health_check()
print(f"Estado de la conexión: {'ACTIVA' if estado else 'INACTIVA'}")

# Simulamos una operación para confirmar que todo funciona
manager.redis_client.set("health:check", "ok")
valor = manager.redis_client.get("health:check")
print(f"Prueba de operación: {valor}")

# El health_check usa PING internamente
ping_result = manager.redis_client.ping()
print(f"Resultado de PING: {ping_result}")

manager.close()
print("\nConexión cerrada correctamente")
