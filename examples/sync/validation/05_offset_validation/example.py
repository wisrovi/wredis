"""Offset validation for bitmap operations."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_offset

# Offset zero: first bit of the bitmap
validate_offset(0)
print("Offset 0: valid")

# Small positive offset
validate_offset(42)
print("Offset 42: valid")

# Large offset (within a large bitmap)
validate_offset(1000000)
print("Offset 1000000: valid")

# Negative offset (invalid case)
try:
    validate_offset(-1)
    print("Offset -1: valid (unexpected)")
except ValidationError as e:
    print(f"Offset -1: invalid -> {e}")

print("\nDemonstrated offset validation for bitmaps.")
