"""Serialization of tuples and their conversion to lists.

This example shows how Python tuples are converted to JSON lists
during serialization, since JSON does not have a type equivalent to tuples.
"""

from wredis._serializer import deserialize, serialize

# Simple tuple
my_tuple = (1, 2, 3)
serialized = serialize(my_tuple)
print(f"Original tuple: {my_tuple} (type: {type(my_tuple).__name__})")
print(f"Serialized: {serialized}")
restored = deserialize(serialized)
print(f"Deserialized: {restored} (type: {type(restored).__name__})")
print()

# Nested tuple
nested_tuple = ((1, 2), (3, 4), (5, 6))
serialized = serialize(nested_tuple)
print(f"Nested tuple: {nested_tuple}")
print(f"Serialized: {serialized}")
restored = deserialize(serialized)
print(f"Deserialized: {restored}")
print()

# Tuple as dictionary value
coordinates = {
    "origin": (0, 0),
    "destination": (10, 20),
    "intermediate_points": [(2, 4), (5, 8), (7, 15)],
}
serialized = serialize(coordinates)
print(f"Coordinates: {coordinates}")
print(f"Serialized: {serialized}")
restored = deserialize(serialized)
print(f"Deserialized: {restored}")
print(f"Type of 'origin': {type(restored['origin']).__name__}")
