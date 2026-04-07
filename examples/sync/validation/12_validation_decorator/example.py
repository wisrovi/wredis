"""Reusable decorator for validating parameters before executing operations."""

from functools import wraps

from wredis._exceptions import ValidationError
from wredis._validation import validate_key, validate_ttl


def validate_set_params(func):
    """Decorator that validates key and ttl before executing a SET function."""

    @wraps(func)
    def wrapper(key: str, value, ttl: int = -1, *args, **kwargs):
        # Validate key before executing
        validate_key(key)
        # Validate TTL before executing
        validate_ttl(ttl)
        return func(key, value, ttl, *args, **kwargs)

    return wrapper


@validate_set_params
def simulate_set(key: str, value, ttl: int = -1):
    """Simulates a Redis SET operation with automatic validation."""
    ttl_desc = "no expiration" if ttl == -1 else f"{ttl}s"
    print(f"  SET {key} = {value} (TTL: {ttl_desc})")
    return True


print("=== Valid operations ===")
simulate_set("user:1", {"name": "Ana"}, ttl=3600)
simulate_set("config:app", {"theme": "dark"}, ttl=-1)
simulate_set("temp:data", "temporary_value", ttl=60)

print("\n=== Invalid operations ===")

try:
    simulate_set("", "value", ttl=3600)
except ValidationError as e:
    print(f"  Error with empty key: {e}")

try:
    simulate_set("user:2", "value", ttl=-5)
except ValidationError as e:
    print(f"  Error with invalid TTL: {e}")

print("\nDemonstrated use of a decorator for automatic validation.")
