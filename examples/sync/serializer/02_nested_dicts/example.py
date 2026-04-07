"""Serialization of nested dictionaries.

This example shows how to serialize complex data structures
with nested dictionaries, commonly used to store configurations
or records in Redis.
"""

from wredis._serializer import deserialize, serialize

# Nested dictionary with user configuration
user = {
    "id": 1001,
    "name": "Ana Garcia",
    "email": "ana@example.com",
    "preferences": {
        "theme": "dark",
        "language": "es",
        "notifications": {
            "email": True,
            "push": False,
            "sms": True,
        },
    },
    "roles": ["admin", "editor"],
}

# Serialize the complete dictionary
serialized = serialize(user)
print("Original dictionary:")
print(f"  {user}")
print(f"\nSerialized ({len(serialized)} characters):")
print(f"  {serialized}")

# Deserialize and verify integrity
restored = deserialize(serialized)
print(f"\nDeserialized:")
print(f"  {restored}")
print(f"\nIs data equal? {user == restored}")
