"""Round-trip data test.

This example verifies that serialized and then deserialized data
is identical to the original, guaranteeing the integrity of the
serialization process.
"""

from wredis._serializer import deserialize, serialize

# Test cases for round-trip
test_cases = [
    ("integer", 42),
    ("float", 3.14159),
    ("string", "hello world"),
    ("boolean_true", True),
    ("boolean_false", False),
    ("none", None),
    ("empty_list", []),
    ("empty_dict", {}),
    ("nested_list", [[1, 2], [3, 4], [5, 6]]),
    ("nested_dict", {"a": {"b": {"c": "deep"}}}),
    ("mixed", [1, "two", 3.0, True, None, {"six": 6}]),
]

print("Round-trip tests:")
print("=" * 60)

all_ok = True
for name, value in test_cases:
    serialized = serialize(value)
    restored = deserialize(serialized)
    is_equal = value == restored
    status = "OK" if is_equal else "FAIL"
    if not is_equal:
        all_ok = False
    print(f"  {name:20s} | {status:5s} | {value!r:40s}")

print("=" * 60)
print(f"Result: {'ALL TESTS PASSED' if all_ok else 'SOME TESTS FAILED'}")
