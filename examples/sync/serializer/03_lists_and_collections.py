"""Serialización de listas y colecciones.

Este ejemplo demuestra la serialización de listas, incluyendo
listas vacías, listas de tipos mixtos y listas anidadas.
"""

from wredis._serializer import serialize, deserialize

# Lista simple de enteros
numeros = [1, 2, 3, 4, 5]
serialized = serialize(numeros)
print(f"Lista de enteros: {numeros}")
print(f"Serializado: {serialized}")
print(f"Deserializado: {deserialize(serialized)}")
print()

# Lista con tipos mixtos
mixta = [42, "texto", 3.14, True, None]
serialized = serialize(mixta)
print(f"Lista mixta: {mixta}")
print(f"Serializado: {serialized}")
print(f"Deserializado: {deserialize(serialized)}")
print()

# Lista anidada (matriz)
matriz = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
serialized = serialize(matriz)
print(f"Matriz: {matriz}")
print(f"Serializado: {serialized}")
print(f"Deserializado: {deserialize(serialized)}")
print()

# Lista vacía
vacia = []
serialized = serialize(vacia)
print(f"Lista vacía: {vacia}")
print(f"Serializado: {serialized}")
print(f"Deserializado: {deserialize(serialized)}")
