"""Basic serialization of Python primitive types.

This example demonstrates how to serialize and deserialize basic
Python types: integers, floats, strings, and booleans.
"""

from wredis._serializer import deserialize, serialize

# Serialize an integer
num = 42
serialized = serialize(num)
print(f"Original integer: {num}")
print(f"Serialized: {serialized!r}")
print(f"Deserialized: {deserialize(serialized)}")
print()

# Serialize a float
pi = 3.14159
serialized = serialize(pi)
print(f"Original float: {pi}")
print(f"Serialized: {serialized!r}")
print(f"Deserialized: {deserialize(serialized)}")
print()

# Serialize a string
text = "hello world"
serialized = serialize(text)
print(f"Original string: {text}")
print(f"Serialized: {serialized!r}")
print(f"Deserialized: {deserialize(serialized)}")
print()

# Serialize a boolean
active = True
serialized = serialize(active)
print(f"Original boolean: {active}")
print(f"Serialized: {serialized!r}")
print(f"Deserialized: {deserialize(serialized)}")
