"""Serialization of None values and their behavior.

This example demonstrates how the value None is serialized and
deserialized, as well as its use in data structures where some
fields may be absent.
"""

from wredis._serializer import deserialize, serialize

# Serialize None directly
null = None
serialized = serialize(null)
print(f"Original None: {null}")
print(f"Serialized: {serialized!r}")
print(f"Deserialized: {deserialize(serialized)}")
print(f"Is it None? {deserialize(serialized) is None}")
print()

# None inside a dictionary
data_with_nulls = {
    "first_name": "Carlos",
    "last_name": "Lopez",
    "middle_name": None,
    "phone": None,
    "email": "carlos@example.com",
}
serialized = serialize(data_with_nulls)
print(f"Dictionary with nulls: {data_with_nulls}")
print(f"Serialized: {serialized}")
restored = deserialize(serialized)
print(f"Deserialized: {restored}")
print(f"Is middle_name None? {restored['middle_name'] is None}")
print()

# None inside a list
list_with_nulls = [1, None, "text", None, True]
serialized = serialize(list_with_nulls)
print(f"List with nulls: {list_with_nulls}")
print(f"Serialized: {serialized}")
print(f"Deserialized: {deserialize(serialized)}")
