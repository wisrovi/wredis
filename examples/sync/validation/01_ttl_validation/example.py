"""Basic TTL validation with acceptable values."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_ttl

# Valid positive TTL: key expires in 3600 seconds (1 hour)
validate_ttl(3600)
print("TTL 3600: valid")

# TTL equal to 0 is also valid (expires immediately)
validate_ttl(0)
print("TTL 0: valid")

# TTL equal to -1 means the key never expires
validate_ttl(-1)
print("TTL -1: valid (no expiration)")

print("\nAll valid TTL values were accepted correctly.")
