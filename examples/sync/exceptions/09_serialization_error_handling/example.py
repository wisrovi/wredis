"""SerializationError handling demonstration.

Shows how to detect and handle serialization and
deserialization errors when interacting with Redis.
"""

import json

from wredis._exceptions import SerializationError


def serialize(data):
    """Serializes data to JSON for storing in Redis.

    Args:
        data: Object to serialize.

    Returns:
        str: JSON serialized data.

    Raises:
        SerializationError: If serialization fails.
    """
    try:
        return json.dumps(data)
    except (TypeError, ValueError) as exc:
        raise SerializationError(
            f"Could not serialize data of type {type(data).__name__}: {exc}"
        ) from exc


def deserialize(text):
    """Deserializes JSON data from Redis.

    Args:
        text: JSON string to deserialize.

    Returns:
        Deserialized object.

    Raises:
        SerializationError: If deserialization fails.
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise SerializationError(f"Could not deserialize: {exc}") from exc


# Case 1: Successful serialization
print("=== Successful serialization ===")
data = {"name": "Ana", "age": 30, "roles": ["admin", "user"]}
try:
    result = serialize(data)
    print(f"Serialized: {result}")
except SerializationError as exc:
    print(f"Error: {exc}")

# Case 2: Non-serializable object
print("\n=== Non-serializable object ===")


class Config:
    def __init__(self):
        self.debug = True


config = Config()
try:
    serialize(config)
except SerializationError as exc:
    print(f"Serialization error: {exc}")
    print(f"  Original cause: {exc.__cause__}")

# Case 3: Corrupted JSON deserialization
print("\n=== Corrupted JSON ===")
corrupted_json = '{name: "Ana", age: }'
try:
    deserialize(corrupted_json)
except SerializationError as exc:
    print(f"Deserialization error: {exc}")

# Case 4: Fallback to default value on error
print("\n=== Fallback on deserialization error ===")
cache_data = ["not json", '{"valid": true}', "not json either"]

for datum in cache_data:
    try:
        result = deserialize(datum)
        print(f"Deserialized: {result}")
    except SerializationError:
        result = None
        print(f"Could not deserialize '{datum}', using None")

# Case 5: Custom serializer with error handling
print("\n=== Custom serializer ===")


def serialize_safe(data, fallback=None):
    """Tries to serialize and returns fallback if it fails.

    Args:
        data: Object to serialize.
        fallback: Value to return if it fails.

    Returns:
        Serialized data or fallback.
    """
    try:
        return serialize(data)
    except SerializationError:
        # Try converting to string as last resort
        try:
            return json.dumps(str(data))
        except Exception:
            return fallback


result = serialize_safe(Config(), fallback='{"error": true}')
print(f"Safe serialization: {result}")
