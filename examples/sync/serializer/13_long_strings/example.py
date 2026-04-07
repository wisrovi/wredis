"""Serialization of very long text strings.

This example demonstrates the behavior of the serializer
with extremely long text strings, such as those that might
be found when storing logs or file contents.
"""

from wredis._serializer import deserialize, serialize

# Create a long string simulating a log
log_lines = [
    f"[2024-01-{i:02d} 10:{i:02d}:00] INFO: Process completed successfully"
    for i in range(1, 101)
]
full_log = "\n".join(log_lines)

print(f"Log length: {len(full_log)} characters")
print(f"First 80 chars: {full_log[:80]}...")

# Serialize
serialized = serialize(full_log)
print(f"\nSerialized size: {len(serialized)} characters")

# Deserialize
restored = deserialize(serialized)
print(f"Deserialized length: {len(restored)} characters")
print(f"Is content intact? {full_log == restored}")
print()

# String with escape characters
text_with_escapes = 'Path: C:\\Users\\admin\\docs\nNew line\tTab\n"Quotes"'
serialized = serialize(text_with_escapes)
print(f"Text with escapes: {text_with_escapes!r}")
print(f"Serialized: {serialized}")
restored = deserialize(serialized)
print(f"Deserialized: {restored!r}")
print(f"Is content intact? {text_with_escapes == restored}")
