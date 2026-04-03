"""Ejemplo 06: Sistema de registro (logging) integrado.

Demuestra el método log() que permite registrar mensajes con
diferentes niveles usando loguru cuando verbose está activado.
"""

import fakeredis

from wredis._base import BaseManager

print("=== Sistema de Logging Integrado ===\n")

# Creamos el manager con verbose=True para habilitar el logging
manager = BaseManager(verbose=True)
manager.redis_client = fakeredis.FakeRedis(decode_responses=True)

# El método log() registra mensajes con diferentes niveles
# Los niveles soportados son: debug, info, warning, error, critical
print("Registrando mensajes con diferentes niveles:\n")

manager.log("Inicializando operaciones de prueba", level="info")
manager.log("Este es un mensaje de depuración", level="debug")
manager.log("Advertencia: operación lenta detectada", level="warning")

# Realizamos operaciones mientras registramos eventos
manager.log("Ejecutando SET", level="debug")
manager.redis_client.set("log:clave", "valor_log")
manager.log("SET completado exitosamente", level="info")

manager.log("Ejecutando GET", level="debug")
valor = manager.redis_client.get("log:clave")
manager.log(f"GET completado - valor: {valor}", level="info")

# Creamos un manager con verbose=False para mostrar que no registra
print("\n--- Manager con verbose=False (sin registros) ---")
manager_silencioso = BaseManager(verbose=False)
manager_silencioso.redis_client = fakeredis.FakeRedis(decode_responses=True)
manager_silencioso.log("Este mensaje NO aparecerá", level="error")
print("El mensaje anterior no se registró porque verbose=False")

manager.close()
manager_silencioso.close()
print("\nConexiones cerradas correctamente")
