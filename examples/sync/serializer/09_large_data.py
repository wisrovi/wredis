"""Serialización de conjuntos de datos grandes.

Este ejemplo demuestra el rendimiento y comportamiento del
serializador al manejar estructuras de datos de gran tamaño,
como listas con miles de elementos o diccionarios extensos.
"""

import sys
from wredis._serializer import serialize, deserialize

# Generar una lista grande con 10,000 elementos
lista_grande = [{"id": i, "valor": f"item_{i}", "activo": i % 2 == 0} for i in range(10000)]

print(f"Lista grande: {len(lista_grande)} elementos")
print(f"Tamaño en memoria (aprox): {sys.getsizeof(lista_grande)} bytes")

# Serializar
serialized = serialize(lista_grande)
print(f"Tamaño serializado: {len(serialized)} caracteres ({len(serialized) / 1024:.1f} KB)")

# Deserializar y verificar
restored = deserialize(serialized)
print(f"Elementos deserializados: {len(restored)}")
print(f"Primer elemento: {restored[0]}")
print(f"Último elemento: {restored[-1]}")
print(f"¿Datos intactos? {lista_grande == restored}")
print()

# Generar un diccionario grande con 5,000 claves
diccionario_grande = {f"clave_{i:04d}": {"valor": i * 1.5, "tipo": "numeric"} for i in range(5000)}

print(f"Diccionario grande: {len(diccionario_grande)} claves")
serialized = serialize(diccionario_grande)
print(f"Tamaño serializado: {len(serialized) / 1024:.1f} KB")
restored = deserialize(serialized)
print(f"Claves deserializadas: {len(restored)}")
print(f"¿Datos intactos? {diccionario_grande == restored}")
