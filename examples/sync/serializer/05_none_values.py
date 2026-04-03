"""Serialización de valores None y su comportamiento.

Este ejemplo demuestra cómo se serializa y deserializa el valor
None, así como su uso en estructuras de datos donde algunos
campos pueden estar ausentes.
"""

from wredis._serializer import serialize, deserialize

# Serializar None directamente
nulo = None
serialized = serialize(nulo)
print(f"None original: {nulo}")
print(f"Serializado: {serialized!r}")
print(f"Deserializado: {deserialize(serialized)}")
print(f"¿Es None? {deserialize(serialized) is None}")
print()

# None dentro de un diccionario
datos_con_nulos = {
    "nombre": "Carlos",
    "apellido": "López",
    "segundo_nombre": None,
    "telefono": None,
    "email": "carlos@ejemplo.com",
}
serialized = serialize(datos_con_nulos)
print(f"Diccionario con nulos: {datos_con_nulos}")
print(f"Serializado: {serialized}")
restored = deserialize(serialized)
print(f"Deserializado: {restored}")
print(f"¿segundo_nombre es None? {restored['segundo_nombre'] is None}")
print()

# None dentro de una lista
lista_con_nulos = [1, None, "texto", None, True]
serialized = serialize(lista_con_nulos)
print(f"Lista con nulos: {lista_con_nulos}")
print(f"Serializado: {serialized}")
print(f"Deserializado: {deserialize(serialized)}")
