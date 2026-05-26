"""Serialization of lists and collections.

This example demonstrates serialization of lists, including
empty lists, mixed-type lists, and nested lists.
"""

from wredis._serializer import deserialize, serialize

# Simple list of integers
numbers = [1, 2, 3, 4, 5]
serialized = serialize(numbers)
print(f"List of integers: {numbers}")
print(f"Serialized: {serialized}")
print(f"Deserialized: {deserialize(serialized)}")
print()

# Mixed-type list
mixed = [42, "text", 3.14, True, None]
serialized = serialize(mixed)
print(f"Mixed list: {mixed}")
print(f"Serialized: {serialized}")
print(f"Deserialized: {deserialize(serialized)}")
print()

# Nested list (matrix)
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
serialized = serialize(matrix)
print(f"Matrix: {matrix}")
print(f"Serialized: {serialized}")
print(f"Deserialized: {deserialize(serialized)}")
print()

# Empty list
empty = []
serialized = serialize(empty)
print(f"Empty list: {empty}")
print(f"Serialized: {serialized}")
print(f"Deserialized: {deserialize(serialized)}")
