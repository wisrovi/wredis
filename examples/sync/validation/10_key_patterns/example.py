"""Key validation with different naming patterns used in Redis."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_key

# Common naming patterns in Redis
patterns = [
    "user:1000",  # entity:id pattern
    "session:abc123:token",  # hierarchical pattern with 3 levels
    "cache:api:github:users",  # cache pattern with source
    "rate_limit:192.168.1.1",  # pattern with IP address
    "queue:emails:pending",  # queue pattern
    "counter:page:home:visits",  # counter pattern
    "lock:resource:database",  # distributed lock pattern
    "config:app:database:url",  # configuration pattern
    "index:user:email:juan@example.com",  # pattern with email (special chars)
    "temp:data_2024-01-15",  # temporal pattern with date
]

print("Validating common Redis key naming patterns:\n")

for pattern in patterns:
    try:
        validate_key(pattern)
        print(f"  [OK] '{pattern}'")
    except ValidationError as e:
        print(f"  [ERR] '{pattern}' -> {e}")

print(f"\n{len(patterns)} naming patterns validated.")
