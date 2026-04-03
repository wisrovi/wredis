"""Serialización de tuplas y su conversión a listas.

Este ejemplo muestra cómo las tuplas de Python se convierten
a listas JSON durante la serialización, ya que JSON no tiene
un tipo equivalente a las tuplas.
"""

from wredis._serializer import serialize, deserialize

# Tupla simple
tupla = (1, 2, 3)
serialized = serialize(tupla)
print(f"Tupla original: {tupla} (tipo: {type(tupla).__name__})")
print(f"Serializado: {serialized}")
restored = deserialize(serialized)
print(f"Deserializado: {restored} (tipo: {type(restored).__name__})")
print()

# Tupla anidada
tupla_anidada = ((1, 2), (3, 4), (5, 6))
serialized = serialize(tupla_anidada)
print(f"Tupla anidada: {tupla_anidada}")
print(f"Serializado: {serialized}")
restored = deserialize(serialized)
print(f"Deserializado: {restored}")
print()

# Tupla como valor en diccionario
coordenadas = {
    "origen": (0, 0),
    "destino": (10, 20),
    "puntos_intermedios": [(2, 4), (5, 8), (7, 15)],
}
serialized = serialize(coordenadas)
print(f"Coordenadas: {coordenadas}")
print(f"Serializado: {serialized}")
restored = deserialize(serialized)
print(f"Deserializado: {restored}")
print(f"Tipo de 'origen': {type(restored['origen']).__name__}")
