"""ValidationError handling demonstration.

Shows how to use ValidationError to validate data before
sending it to Redis and handle validation errors.
"""

from wredis._exceptions import ValidationError


def validate_redis_key(key):
    """Validates that a Redis key meets basic rules.

    Args:
        key: The key to validate.

    Raises:
        ValidationError: If the key is invalid.
    """
    if not key:
        raise ValidationError("Key cannot be empty")
    if not isinstance(key, str):
        raise ValidationError(f"Key must be str, not {type(key).__name__}")
    if len(key) > 512:
        raise ValidationError(f"Key exceeds 512 characters (has {len(key)})")
    if " " in key:
        raise ValidationError("Key cannot contain spaces")
    return True


def validate_value_for_set(key, value):
    """Validates a key-value pair before a SET.

    Args:
        key: The Redis key.
        value: The value to store.

    Raises:
        ValidationError: If validation fails.
    """
    validate_redis_key(key)
    if value is None:
        raise ValidationError(f"Cannot store None in '{key}'")


# Case 1: Empty key
try:
    validate_redis_key("")
except ValidationError as exc:
    print(f"Validation error: {exc}")

# Case 2: Key with spaces
try:
    validate_redis_key("my key with spaces")
except ValidationError as exc:
    print(f"Validation error: {exc}")

# Case 3: Wrong type
try:
    validate_redis_key(12345)
except ValidationError as exc:
    print(f"Validation error: {exc}")

# Case 4: None value
try:
    validate_value_for_set("user:1", None)
except ValidationError as exc:
    print(f"Validation error: {exc}")

# Case 5: Successful validation
try:
    validate_value_for_set("user:1", {"name": "Ana"})
    print("Validation successful: key and value are correct")
except ValidationError as exc:
    print(f"Validation error: {exc}")

# Case 6: Key too long
try:
    validate_redis_key("a" * 600)
except ValidationError as exc:
    print(f"Validation error: {exc}")
