"""Score validation with different Python numeric types."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_score

# Positive integer
validate_score(42)
print("Positive int (42): valid")

# Negative integer
validate_score(-42)
print("Negative int (-42): valid")

# Zero integer
validate_score(0)
print("Zero int (0): valid")

# Positive float
validate_score(3.14)
print("Positive float (3.14): valid")

# Negative float
validate_score(-2.718)
print("Negative float (-2.718): valid")

# Boolean: in Python bool is subclass of int, so True=1 and False=0 are valid
validate_score(True)
print("bool True (equals 1): valid")

validate_score(False)
print("bool False (equals 0): valid")

# Invalid type: string
try:
    validate_score("100")
    print("str '100': valid (unexpected)")
except ValidationError as e:
    print(f"str '100': invalid -> {e}")

# Invalid type: None
try:
    validate_score(None)
    print("None: valid (unexpected)")
except ValidationError as e:
    print(f"None: invalid -> {e}")

# Invalid type: list
try:
    validate_score([1, 2, 3])
    print("list: valid (unexpected)")
except ValidationError as e:
    print(f"list: invalid -> {e}")

print("\nDemonstrated score validation with different numeric types.")
