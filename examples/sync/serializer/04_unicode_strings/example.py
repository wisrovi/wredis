"""Serialization of Unicode text and special characters.

This example shows how the serializer correctly handles
Unicode characters, emojis, and special characters from
various languages thanks to ensure_ascii=False.
"""

from wredis._serializer import deserialize, serialize

# Spanish text with accents and eñe
spanish = "El nino juego en el jardin con su mama"
serialized = serialize(spanish)
print(f"Spanish: {spanish}")
print(f"Serialized: {serialized}")
print(f"Deserialized: {deserialize(serialized)}")
print()

# Japanese text
japanese = "こんにちは世界"
serialized = serialize(japanese)
print(f"Japanese: {japanese}")
print(f"Serialized: {serialized}")
print(f"Deserialized: {deserialize(serialized)}")
print()

# Text with emojis
emojis = "Python is great 🐍✨🚀"
serialized = serialize(emojis)
print(f"Emojis: {emojis}")
print(f"Serialized: {serialized}")
print(f"Deserialized: {deserialize(serialized)}")
print()

# Special characters and symbols
symbols = "Price: €100 | ¥500 | £75 | © 2024"
serialized = serialize(symbols)
print(f"Symbols: {symbols}")
print(f"Serialized: {serialized}")
print(f"Deserialized: {deserialize(serialized)}")
