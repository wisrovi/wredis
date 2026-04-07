"""TTL validation with invalid values that raise ValidationError."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_ttl

# Try to validate a TTL less than -1 (invalid)
invalid_ttls = [-2, -10, -100, -999]

for ttl in invalid_ttls:
    try:
        validate_ttl(ttl)
        print(f"TTL {ttl}: valid (unexpected)")
    except ValidationError as e:
        print(f"TTL {ttl}: invalid -> {e}")

print("\nDemonstrated that TTLs less than -1 raise ValidationError.")
