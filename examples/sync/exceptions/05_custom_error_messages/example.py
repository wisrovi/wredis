"""Custom error messages in exceptions demonstration.

Shows how to create and throw WRedis exceptions with detailed
messages and additional attributes for diagnosis.
"""

from wredis._exceptions import OperationError, ValidationError, WRedisError

# Throw exceptions with descriptive messages
try:
    raise ValidationError("Field 'email' is not in a valid format: 'user@'")
except ValidationError as exc:
    print(f"Validation failed: {exc}")


# Create exceptions with additional context using args
try:
    error = OperationError("Could not execute GET")
    error.key = "user:1234"
    error.operation = "GET"
    raise error
except OperationError as exc:
    print(f"\nOperation: {exc.operation}")
    print(f"Affected key: {exc.key}")
    print(f"Original message: {exc}")


# Custom subclass with personalized attributes for better diagnosis
class ErrorWithContext(WRedisError):
    """Exception that stores additional context for debugging.

    Attributes:
        operation: Name of the operation that failed.
        details: Dictionary with contextual information.
    """

    def __init__(self, message, operation=None, details=None):
        super().__init__(message)
        self.operation = operation
        self.details = details or {}

    def __str__(self):
        base = super().__str__()
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{base} [{details_str}]"
        return base


try:
    raise ErrorWithContext(
        "Timeout expired",
        operation="HGETALL",
        details={"key": "session:abc", "timeout": "5s", "retries": 3},
    )
except ErrorWithContext as exc:
    print(f"\nError with context: {exc}")
    print(f"  Operation: {exc.operation}")
    print(f"  Details: {exc.details}")


# Format messages dynamically
key = "product:999"
value = {"name": "Widget", "price": None}

try:
    raise ValidationError(f"Cannot serialize value for '{key}': field 'price' cannot be null")
except ValidationError as exc:
    print(f"\n{exc}")
