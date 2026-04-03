"""Ejemplo 01: Inicialización básica de BaseManager.

Demuestra cómo crear una instancia de BaseManager con los parámetros
por defecto y verificar que la conexión funciona usando fakeredis.
"""

import fakeredis

from wredis._base import BaseManager

# Creamos una instancia con configuración por defecto
# Los valores por defecto son: host=localhost, port=6379, db=0
manager = BaseManager()

# Reemplazamos el cliente con FakeRedis para pruebas sin servidor real
manager.redis_client = fakeredis.FakeRedis(decode_responses=True)

# Verificamos que el cliente está conectado
print(f"Cliente Redis creado: {type(manager.redis_client).__name__}")
print(f"Modo verbose activado: {manager.verbose}")

# Hacemos una operación básica para confirmar que funciona
manager.redis_client.set("ejemplo:01", "inicializacion_basica")
resultado = manager.redis_client.get("ejemplo:01")
print(f"Valor almacenado y recuperado: {resultado}")

# Limpiamos recursos
manager.close()
print("Conexión cerrada correctamente")
