"""Bit value validation (0 and 1) for SETBIT/GETBIT operations."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_bit_value

# Valid bit value: 0
validate_bit_value(0)
print("Bit 0: valid")

# Valid bit value: 1
validate_bit_value(1)
print("Bit 1: valid")

# Invalid bit values
invalid_values = [-1, 2, 3, 100, 999]

for value in invalid_values:
    try:
        validate_bit_value(value)
        print(f"Bit {value}: valid (unexpected)")
    except ValidationError as e:
        print(f"Bit {value}: invalid -> {e}")

print("\nDemonstrated that only 0 and 1 are valid values for bits.")
