"""Validation of multiple fields in a single operation (batch validation)."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_bit_value, validate_key, validate_offset, validate_score, validate_ttl


def validate_bitmap_operation(key: str, offset: int, bit_value: int) -> bool:
    """Validates all parameters for a bitmap operation."""
    errors = []

    # Validate each field individually
    try:
        validate_key(key)
    except ValidationError as e:
        errors.append(str(e))

    try:
        validate_offset(offset)
    except ValidationError as e:
        errors.append(str(e))

    try:
        validate_bit_value(bit_value)
    except ValidationError as e:
        errors.append(str(e))

    return errors


# Valid case: all parameters correct
errors = validate_bitmap_operation("user:flags", 0, 1)
if errors:
    print(f"Errors: {errors}")
else:
    print("Valid bitmap operation: key='user:flags', offset=0, bit=1")

# Invalid case: multiple errors
errors = validate_bitmap_operation("", -5, 3)
if errors:
    print(f"Invalid operation with {len(errors)} errors:")
    for error in errors:
        print(f"  - {error}")

# Partially invalid case: only the bit is incorrect
errors = validate_bitmap_operation("user:flags", 100, 2)
if errors:
    print(f"Operation with 1 error: {errors[0]}")

print("\nDemonstrated batch validation of multiple parameters.")
