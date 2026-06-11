"""Basic Redis key validation with valid cases."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_key

# Simple short key
validate_key("user:123")
print("Key 'user:123': valid")

# Key with hierarchical prefix
validate_key("app:sessions:token_abc")
print("Key 'app:sessions:token_abc': valid")

# Key with allowed special characters
validate_key("cache:data_v2.0")
print("Key 'cache:data_v2.0': valid")

# Key with single character (minimum valid)
validate_key("x")
print("Key 'x': valid")

# Key with exactly 512 characters (maximum limit)
long_key = "k" * 512
validate_key(long_key)
print("Key with 512 characters: valid")

print("\nAll valid keys were accepted correctly.")
