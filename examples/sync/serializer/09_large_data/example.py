"""Serialization of large datasets.

This example demonstrates the performance and behavior of the
serializer when handling large data structures, such as lists
with thousands of elements or extensive dictionaries.
"""

import sys

from wredis._serializer import deserialize, serialize

# Generate a large list with 10,000 elements
large_list = [{"id": i, "value": f"item_{i}", "active": i % 2 == 0} for i in range(10000)]

print(f"Large list: {len(large_list)} elements")
print(f"Size in memory (approx): {sys.getsizeof(large_list)} bytes")

# Serialize
serialized = serialize(large_list)
print(f"Serialized size: {len(serialized)} characters ({len(serialized) / 1024:.1f} KB)")

# Deserialize and verify
restored = deserialize(serialized)
print(f"Deserialized elements: {len(restored)}")
print(f"First element: {restored[0]}")
print(f"Last element: {restored[-1]}")
print(f"Is data intact? {large_list == restored}")
print()

# Generate a large dictionary with 5,000 keys
large_dict = {f"key_{i:04d}": {"value": i * 1.5, "type": "numeric"} for i in range(5000)}

print(f"Large dictionary: {len(large_dict)} keys")
serialized = serialize(large_dict)
print(f"Serialized size: {len(serialized) / 1024:.1f} KB")
restored = deserialize(serialized)
print(f"Deserialized keys: {len(restored)}")
print(f"Is data intact? {large_dict == restored}")
