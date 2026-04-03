"""Serialización de texto Unicode y caracteres especiales.

Este ejemplo muestra cómo el serializador maneja correctamente
caracteres Unicode, emojis y caracteres especiales de diversos
idiomas gracias a ensure_ascii=False.
"""

from wredis._serializer import serialize, deserialize

# Texto en español con acentos y eñe
espanol = "El niño jugó en el jardín con su mamá"
serialized = serialize(espanol)
print(f"Español: {espanol}")
print(f"Serializado: {serialized}")
print(f"Deserializado: {deserialize(serialized)}")
print()

# Texto en japonés
japones = "こんにちは世界"
serialized = serialize(japones)
print(f"Japonés: {japones}")
print(f"Serializado: {serialized}")
print(f"Deserializado: {deserialize(serialized)}")
print()

# Texto con emojis
emojis = "Python es genial 🐍✨🚀"
serialized = serialize(emojis)
print(f"Emojis: {emojis}")
print(f"Serializado: {serialized}")
print(f"Deserializado: {deserialize(serialized)}")
print()

# Caracteres especiales y símbolos
simbolos = "Precio: €100 | ¥500 | £75 | © 2024"
serialized = serialize(simbolos)
print(f"Símbolos: {simbolos}")
print(f"Serializado: {serialized}")
print(f"Deserializado: {deserialize(serialized)}")
