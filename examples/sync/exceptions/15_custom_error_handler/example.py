"""Custom error handler creation demonstration.

Shows how to design classes and functions to handle
WRedis exceptions in a centralized and reusable way.
"""

from wredis._exceptions import (
    CacheError,
    ClusterError,
    OperationError,
    PubSubError,
    QueueError,
    RedisConnectionError,
    SentinelError,
    SerializationError,
    StreamError,
    TransactionError,
    ValidationError,
    WRedisError,
)


class WRedisErrorHandler:
    """Centralized handler for WRedis exceptions.

    Allows registering callbacks for each error type and
    executing specific actions automatically.
    """

    def __init__(self):
        self._handlers = {}
        self._default_handler = None
        self._history = []

    def register(self, error_type, handler):
        """Registers a handler for an error type.

        Args:
            error_type: Exception class to handle.
            handler: Function that receives the exception and returns a value.
        """
        self._handlers[error_type] = handler

    def register_default(self, handler):
        """Registers a default handler for unregistered errors.

        Args:
            handler: Default handler function.
        """
        self._default_handler = handler

    def handle(self, exc):
        """Executes the corresponding handler for an exception.

        Args:
            exc: The caught exception.

        Returns:
            The result of the handler or None.
        """
        self._history.append(exc)
        handler = self._handlers.get(type(exc))
        if handler is None:
            # Look for handler for parent classes
            for err_type, h in self._handlers.items():
                if isinstance(exc, err_type):
                    handler = h
                    break
        if handler is None:
            handler = self._default_handler
        if handler:
            return handler(exc)
        return None

    @property
    def history(self):
        return list(self._history)


# Configure the handler
handler = WRedisErrorHandler()

# Register specific handlers
handler.register(
    RedisConnectionError,
    lambda exc: f"[RECONNECT] {exc} - Attempting reconnection...",
)
handler.register(
    ValidationError,
    lambda exc: f"[VALIDATE] {exc} - Requesting corrected data",
)
handler.register(
    SerializationError,
    lambda exc: f"[SERIALIZE] {exc} - Using alternative serializer",
)
handler.register(
    TransactionError,
    lambda exc: f"[RETRY] {exc} - Retrying transaction",
)
handler.register(
    QueueError,
    lambda exc: f"[QUEUE] {exc} - Discarding old message",
)

# Default handler
handler.register_default(lambda exc: f"[GENERIC] {type(exc).__name__}: {exc}")


# Simulate operations and handle errors
def simulate_error(error_type):
    raise error_type(f"Simulated error from {error_type.__name__}")


errors_to_test = [
    RedisConnectionError,
    ValidationError,
    SerializationError,
    TransactionError,
    QueueError,
    CacheError,
    PubSubError,
    StreamError,
]

print("=== Custom error handlers ===\n")

for tipo in errors_to_test:
    try:
        simulate_error(tipo)
    except WRedisError as exc:
        result = handler.handle(exc)
        print(f"  {result}")

# Show history
print(f"\n=== Error history ({len(handler.history)}) ===")
for i, err in enumerate(handler.history, 1):
    print(f"  {i}. {type(err).__name__}: {err}")


# Decorator pattern for automatic handling
print("\n=== @handle_errors decorator ===")


def handle_errors(handler_func):
    """Decorator that catches WRedisError and passes it to the handler.

    Args:
        handler_func: Function that receives (exc, func_name, args, kwargs).

    Returns:
        Decorator.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except WRedisError as exc:
                return handler_func(exc, func.__name__, args, kwargs)

        return wrapper

    return decorator


def my_handler(exc, func_name, args, kwargs):
    return f"Error in {func_name}: {type(exc).__name__} - {exc}"


@handle_errors(my_handler)
def get_user(user_id):
    if user_id < 0:
        raise ValidationError(f"Invalid ID: {user_id}")
    return {"id": user_id}


@handle_errors(my_handler)
def connect_redis():
    raise RedisConnectionError("Server unavailable")


print(get_user(-1))
print(connect_redis())
print(get_user(42))  # Successful case
