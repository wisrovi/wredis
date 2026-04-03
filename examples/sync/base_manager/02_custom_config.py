"""Ejemplo 02: Configuración personalizada de BaseManager.

Demuestra cómo inicializar BaseManager con parámetros personalizados
como host, puerto, base de datos, timeout y número máximo de conexiones.
"""

import fakeredis

from wredis._base import BaseManager

# Configuración personalizada para un entorno de producción simulado
manager = BaseManager(
    host="redis.produccion.local",
    port=6380,
    db=5,
    password="secreto123",
    socket_timeout=10.0,
    max_connections=20,
    decode_responses=True,
    verbose=False,
)

# Reemplazamos con FakeRedis para las pruebas
manager.redis_client = fakeredis.FakeRedis(decode_responses=True)

# Mostramos la configuración aplicada
print("Configuración personalizada de BaseManager:")
print(f"  Host: redis.produccion.local")
print(f"  Puerto: 6380")
print(f"  Base de datos: 5")
print(f"  Timeout de socket: 10.0s")
print(f"  Máximo de conexiones: 20")
print(f"  Decodificar respuestas: True")
print(f"  Verbose: {manager.verbose}")

# Verificamos que funciona con la configuración
manager.redis_client.set("config:entorno", "produccion_simulada")
valor = manager.redis_client.get("config:entorno")
print(f"\nPrueba de escritura/lectura: {valor}")

manager.close()
print("Conexión cerrada correctamente")
