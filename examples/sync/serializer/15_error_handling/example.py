"""Advanced error handling and data validation.

This example shows advanced techniques for handling serialization
errors, including prior data validation and graceful recovery
on failures.
"""

from wredis._exceptions import SerializationError
from wredis._serializer import deserialize, serialize


# Safe serialization function with default value
def serialize_safe(value, default_value="{}"):
    """Safely serializes a value, returning a default if it fails."""
    try:
        return serialize(value)
    except SerializationError as e:
        print(f"  [WARNING] Serialization failed: {e}")
        return default_value


# Safe deserialization function
def deserialize_safe(data, default_value=None):
    """Safely deserializes data, returning a default if it fails."""
    try:
        return deserialize(data)
    except SerializationError as e:
        print(f"  [WARNING] Deserialization failed: {e}")
        return default_value


# Tests with valid data
print("1. Valid data:")
result = serialize_safe({"name": "test", "value": 42})
print(f"  Safe serialized: {result}")
print(f"  Deserialized: {deserialize_safe(result)}")
print()

# Tests with invalid data
print("2. Invalid data (non-serializable set):")
result = serialize_safe({1, 2, 3})
print(f"  Default value returned: {result}")
print()

print("3. Invalid JSON to deserialize:")
result = deserialize_safe("{broken json}")
print(f"  Default value returned: {result}")
print()


# Prior validation before serializing
def is_serializable(value):
    """Checks if a value can be serialized without throwing an exception."""
    try:
        serialize(value)
        return True
    except SerializationError:
        return False


print("4. Prior validation:")
valid_data = {"list": [1, 2, 3], "text": "hello"}
invalid_data = {"function": lambda x: x}
print(f"  Is valid dict serializable? {is_serializable(valid_data)}")
print(f"  Is dict with lambda serializable? {is_serializable(invalid_data)}")
