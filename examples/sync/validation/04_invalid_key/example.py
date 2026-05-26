"""Key validation with invalid cases: empty and too long."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_key

# Empty key (empty string)
try:
    validate_key("")
    print("Empty key: valid (unexpected)")
except ValidationError as e:
    print(f"Empty key: invalid -> {e}")

# Key with more than 512 characters
very_long_key = "a" * 513
try:
    validate_key(very_long_key)
    print("Key with 513 characters: valid (unexpected)")
except ValidationError as e:
    print(f"Key with 513 characters: invalid -> {e}")

# Extremely long key
huge_key = "b" * 10000
try:
    validate_key(huge_key)
    print("Key with 10000 characters: valid (unexpected)")
except ValidationError as e:
    print(f"Key with 10000 characters: invalid -> {e}")

print(
    "\nDemonstrated that empty keys or keys larger than 512 characters raise ValidationError."
)
