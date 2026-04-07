"""Score validation for sorted sets."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_score

# Positive integer score
validate_score(100)
print("Score 100: valid")

# Negative integer score
validate_score(-50)
print("Score -50: valid")

# Float score
validate_score(3.14159)
print("Score 3.14159: valid")

# Zero score
validate_score(0)
print("Score 0: valid")

# Negative float score
validate_score(-999.99)
print("Score -999.99: valid")

# NaN score (invalid)
try:
    validate_score(float("nan"))
    print("Score NaN: valid (unexpected)")
except ValidationError as e:
    print(f"Score NaN: invalid -> {e}")

# Positive infinity (invalid)
try:
    validate_score(float("inf"))
    print("Score inf: valid (unexpected)")
except ValidationError as e:
    print(f"Score inf: invalid -> {e}")

# Negative infinity (invalid)
try:
    validate_score(float("-inf"))
    print("Score -inf: valid (unexpected)")
except ValidationError as e:
    print(f"Score -inf: invalid -> {e}")

print("\nDemonstrated score validation for sorted sets.")
