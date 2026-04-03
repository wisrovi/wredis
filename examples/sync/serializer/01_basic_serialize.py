"""Serialización básica de tipos primitivos de Python.

Este ejemplo demuestra cómo serializar y deserializar los tipos
básicos de Python: enteros, flotantes, cadenas y booleanos.
"""

from wredis._serializer import serialize, deserialize

# Serializar un entero
num = 42
serialized = serialize(num)
print(f"Entero original: {num}")
print(f"Serializado: {serialized!r}")
print(f"Deserializado: {deserialize(serialized)}")
print()

# Serializar un flotante
pi = 3.14159
serialized = serialize(pi)
print(f"Flotante original: {pi}")
print(f"Serializado: {serialized!r}")
print(f"Deserializado: {deserialize(serialized)}")
print()

# Serializar una cadena
texto = "hola mundo"
serialized = serialize(texto)
print(f"Cadena original: {texto}")
print(f"Serializado: {serialized!r}")
print(f"Deserializado: {deserialize(serialized)}")
print()

# Serializar un booleano
activo = True
serialized = serialize(activo)
print(f"Booleano original: {activo}")
print(f"Serializado: {serialized!r}")
print(f"Deserializado: {deserialize(serialized)}")
