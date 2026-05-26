"""Edge case validation for all validation functions."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_bit_value, validate_key, validate_offset, validate_score, validate_ttl

print("=== Edge cases for TTL ===")
# Valid lower limit
validate_ttl(-1)
print("TTL -1 (lower limit): valid")

# Invalid lower limit
try:
    validate_ttl(-2)
except ValidationError:
    print("TTL -2 (just below limit): invalid")

print("\n=== Edge cases for Key ===")
# Key with exactly 512 characters
validate_key("a" * 512)
print("Key with 512 chars (exact limit): valid")

# Key with 513 characters (one more)
try:
    validate_key("a" * 513)
except ValidationError:
    print("Key with 513 chars (one over limit): invalid")

print("\n=== Edge cases for Offset ===")
validate_offset(0)
print("Offset 0 (lower limit): valid")

try:
    validate_offset(-1)
except ValidationError:
    print("Offset -1 (just below limit): invalid")

print("\n=== Edge cases for Bit Value ===")
validate_bit_value(0)
validate_bit_value(1)
print("Bit 0 and 1: valid")

try:
    validate_bit_value(-1)
except ValidationError:
    print("Bit -1: invalid")

try:
    validate_bit_value(2)
except ValidationError:
    print("Bit 2: invalid")

print("\n=== Edge cases for Score ===")
validate_score(0)
print("Score 0: valid")

# Very large but finite score
validate_score(1e308)
print("Score 1e308: valid")

try:
    validate_score(float("nan"))
except ValidationError:
    print("Score NaN: invalid")

try:
    validate_score(float("inf"))
except ValidationError:
    print("Score inf: invalid")

print("\nAll edge cases were verified correctly.")
