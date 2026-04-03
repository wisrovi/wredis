"""Manejo avanzado de errores y validación de datos.

Este ejemplo muestra técnicas avanzadas para manejar errores
de serialización, incluyendo validación previa de datos y
recuperación graceful ante fallos.
"""

from wredis._serializer import serialize, deserialize
from wredis._exceptions import SerializationError


# Función segura de serialización con valor por defecto
def serializar_seguro(valor, valor_defecto="{}"):
    """Serializa un valor de forma segura, retornando un valor por defecto si falla."""
    try:
        return serialize(valor)
    except SerializationError as e:
        print(f"  [AVISO] Serialización fallida: {e}")
        return valor_defecto


# Función segura de deserialización
def deserializar_seguro(datos, valor_defecto=None):
    """Deserializa datos de forma segura, retornando un valor por defecto si falla."""
    try:
        return deserialize(datos)
    except SerializationError as e:
        print(f"  [AVISO] Deserialización fallida: {e}")
        return valor_defecto


# Pruebas con datos válidos
print("1. Datos válidos:")
resultado = serializar_seguro({"nombre": "test", "valor": 42})
print(f"  Serializado seguro: {resultado}")
print(f"  Deserializado: {deserializar_seguro(resultado)}")
print()

# Pruebas con datos inválidos
print("2. Datos inválidos (set no serializable):")
resultado = serializar_seguro({1, 2, 3})
print(f"  Valor por defecto retornado: {resultado}")
print()

print("3. JSON inválido para deserializar:")
resultado = deserializar_seguro("{json roto}")
print(f"  Valor por defecto retornado: {resultado}")
print()


# Validación previa antes de serializar
def es_serializable(valor):
    """Verifica si un valor puede ser serializado sin lanzar excepción."""
    try:
        serialize(valor)
        return True
    except SerializationError:
        return False


print("4. Validación previa:")
datos_validos = {"lista": [1, 2, 3], "texto": "hola"}
datos_invalidos = {"funcion": lambda x: x}
print(f"  ¿Dict válido es serializable? {es_serializable(datos_validos)}")
print(f"  ¿Dict con lambda es serializable? {es_serializable(datos_invalidos)}")
