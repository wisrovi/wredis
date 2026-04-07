"""Validation of parameters for bitmap operations."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_bit_value, validate_key, validate_offset


def simulate_setbit(key: str, offset: int, value: int) -> dict:
    """Simulates a SETBIT operation with complete validation."""
    # Validate each parameter individually
    validate_key(key)
    validate_offset(offset)
    validate_bit_value(value)

    return {"key": key, "offset": offset, "value": value, "status": "ok"}


print("=== Valid SETBIT operations ===")

# Set first bit to 1
result = simulate_setbit("user:1:permissions", 0, 1)
print(f"  {result}")

# Set a distant bit to 0
result = simulate_setbit("user:1:permissions", 1024, 0)
print(f"  {result}")

# Set bit at large offset
result = simulate_setbit("analytics:daily:2024", 50000, 1)
print(f"  {result}")

print("\n=== Invalid SETBIT operations ===")

# Empty key
try:
    simulate_setbit("", 0, 1)
except ValidationError as e:
    print(f"  Empty key: {e}")

# Negative offset
try:
    simulate_setbit("user:1:permissions", -1, 1)
except ValidationError as e:
    print(f"  Negative offset: {e}")

# Invalid bit value
try:
    simulate_setbit("user:1:permissions", 0, 2)
except ValidationError as e:
    print(f"  Invalid bit value: {e}")

# Multiple errors
try:
    simulate_setbit("", -5, 3)
except ValidationError as e:
    print(f"  Multiple errors (first detected): {e}")

print("\nDemonstrated complete validation for bitmap operations.")
