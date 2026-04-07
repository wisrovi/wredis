"""Serialization of boolean values and their variants.

This example shows how boolean values True and False are handled,
both individually and within more complex data structures.
"""

from wredis._serializer import deserialize, serialize

# Individual booleans
true_value = True
false_value = False

serialized_true = serialize(true_value)
serialized_false = serialize(false_value)

print(f"True serialized: {serialized_true!r}")
print(f"False serialized: {serialized_false!r}")
print(f"True deserialized: {deserialize(serialized_true)}")
print(f"False deserialized: {deserialize(serialized_false)}")
print()

# Booleans in a configuration dictionary
config = {
    "debug": True,
    "production": False,
    "log_enabled": True,
    "cache_disabled": False,
    "max_retries": 3,
}
serialized = serialize(config)
print(f"Configuration: {config}")
print(f"Serialized: {serialized}")
restored = deserialize(serialized)
print(f"Deserialized: {restored}")
print(f"Type of 'debug': {type(restored['debug']).__name__}")
print()

# List of boolean results
results = [True, False, True, True, False]
serialized = serialize(results)
print(f"Results: {results}")
print(f"Serialized: {serialized}")
print(f"Deserialized: {deserialize(serialized)}")
