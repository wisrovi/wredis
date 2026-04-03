"""Ejemplo 04: Uso de BaseManager como gestor de contexto.

Demuestra cómo usar BaseManager con la sentencia 'with' para
garantizar que los recursos se liberan automáticamente al salir del bloque.
"""

import fakeredis

from wredis._base import BaseManager

print("=== Gestor de Contexto (Context Manager) ===\n")

# Usamos BaseManager como gestor de contexto con 'with'
# Esto asegura que close() se llama automáticamente al salir del bloque
with BaseManager(verbose=False) as manager:
    # Reemplazamos con FakeRedis para las pruebas
    manager.redis_client = fakeredis.FakeRedis(decode_responses=True)

    # Verificamos que la conexión funciona dentro del contexto
    print(f"Dentro del contexto - Cliente: {type(manager.redis_client).__name__}")

    # Realizamos operaciones dentro del contexto
    manager.redis_client.set("contexto:clave", "valor_contexto")
    resultado = manager.redis_client.get("contexto:clave")
    print(f"Valor dentro del contexto: {resultado}")

    # Verificamos salud
    print(f"Health check dentro del contexto: {manager.health_check()}")

# Al salir del bloque 'with', se llama automáticamente a manager.close()
print("\nFuera del contexto - los recursos fueron liberados automáticamente")
print("Conexión cerrada correctamente")
