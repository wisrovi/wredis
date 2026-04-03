"""Manejo de errores en la serialización.

Este ejemplo muestra cómo capturar y manejar excepciones
SerializationError cuando se intenta serializar objetos
que no son compatibles con JSON.
"""

from wredis._serializer import serialize, deserialize
from wredis._exceptions import SerializationError

# Intentar serializar un conjunto (set) - no es serializable en JSON
try:
    conjunto = {1, 2, 3}
    serialize(conjunto)
except SerializationError as e:
    print(f"Error al serializar set: {e}")
print()

# Intentar serializar una función - no es serializable
try:

    def mi_funcion():
        pass

    serialize(mi_funcion)
except SerializationError as e:
    print(f"Error al serializar función: {e}")
print()


# Intentar serializar un objeto complejo personalizado
class MiClase:
    pass


try:
    obj = MiClase()
    serialize(obj)
except SerializationError as e:
    print(f"Error al serializar objeto personalizado: {e}")
print()

# Deserialización con JSON inválido
try:
    deserialize("{esto no es json válido}")
except SerializationError as e:
    print(f"Error al deserializar JSON inválido: {e}")
print()

# Deserialización con entrada no-string
try:
    deserialize(12345)
except SerializationError as e:
    print(f"Error al deserializar no-string: {e}")
