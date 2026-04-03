"""Ejemplo 08: Manejo de errores con BaseManager.

Demuestra cómo manejar errores de conexión y operaciones fallidas
usando las excepciones personalizadas de wredis.
"""

import fakeredis

from wredis._base import BaseManager
from wredis._exceptions import OperationError

print("=== Manejo de Errores ===\n")

# Creamos el manager con FakeRedis
manager = BaseManager(verbose=False)
manager.redis_client = fakeredis.FakeRedis(decode_responses=True)

# Escenario 1: Operación exitosa
print("1. Operación exitosa:")
try:
    resultado = manager._execute("set", "error:clave", "valor")
    print(f"   SET exitoso: {resultado}")
except OperationError as e:
    print(f"   Error inesperado: {e}")

# Escenario 2: Health check exitoso
print("\n2. Health check exitoso:")
try:
    estado = manager.health_check()
    print(f"   Conexión activa: {estado}")
except OperationError as e:
    print(f"   Health check falló: {e}")

# Escenario 3: Operación con datos inválidos (FakeRedis es permisivo,
# pero mostramos la estructura de manejo de errores)
print("\n3. Manejo estructurado de errores:")
try:
    # Intentamos una operación que podría fallar
    manager._execute("get", "error:clave_inexistente")
    print("   GET en clave inexistente: None (comportamiento esperado)")
except OperationError as e:
    print(f"   Error de operación: {e}")

# Escenario 4: Cierre seguro
print("\n4. Cierre seguro de conexión:")
try:
    manager.close()
    print("   Conexión cerrada sin errores")
except Exception as e:
    print(f"   Error al cerrar: {e}")

# Escenario 5: Uso de gestor de contexto para manejo automático de errores
print("\n5. Gestor de contexto para manejo automático:")
try:
    with BaseManager(verbose=False) as m:
        m.redis_client = fakeredis.FakeRedis(decode_responses=True)
        m._execute("set", "context:error", "seguro")
        print("   Operación dentro del contexto: exitosa")
    print("   Recursos liberados automáticamente al salir del contexto")
except OperationError as e:
    print(f"   Error capturado: {e}")

print("\nTodos los escenarios de manejo de errores completados")
