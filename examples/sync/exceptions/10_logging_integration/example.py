"""Exception logging integration demonstration.

Shows how to log WRedis exceptions using Python's standard
logging module for auditing and diagnosis.
"""

import logging
import sys

from wredis._exceptions import CacheError, OperationError, RedisConnectionError, WRedisError

# Configure the logger
logger = logging.getLogger("wredis.examples")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def operation_that_fails(error_type):
    """Simulates an operation that throws a specific error.

    Args:
        error_type: Exception class to raise.

    Raises:
        The specified exception.
    """
    raise error_type(f"Simulated error from {error_type.__name__}")


# Log errors with different severity levels
severe_errors = [RedisConnectionError, OperationError]
mild_errors = [CacheError]

print("=== Logging severe errors ===\n")

for tipo in severe_errors:
    try:
        operation_that_fails(tipo)
    except WRedisError as exc:
        logger.error(
            "Severe error in Redis operation",
            extra={
                "type": type(exc).__name__,
                "message": str(exc),
            },
        )
        logger.debug(f"Traceback: {exc.__traceback__}")

print("\n=== Logging mild errors ===\n")

for tipo in mild_errors:
    try:
        operation_that_fails(tipo)
    except WRedisError as exc:
        logger.warning(
            "Mild error, can continue",
            extra={
                "type": type(exc).__name__,
                "message": str(exc),
            },
        )

# Custom logger that formats WRedis exceptions
print("\n=== Custom logger for WRedisError ===\n")


class WRedisLogger:
    """Specialized logger for WRedis exceptions."""

    def __init__(self, name="wredis"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            h = logging.StreamHandler(sys.stdout)
            h.setFormatter(logging.Formatter("[WREDIS] %(levelname)s: %(message)s"))
            self.logger.addHandler(h)

    def log_error(self, exc, context=None):
        """Logs a WRedis exception with context.

        Args:
            exc: The caught exception.
            context: Optional additional information.
        """
        if not isinstance(exc, WRedisError):
            raise TypeError(f"Expected WRedisError, not {type(exc).__name__}")

        message = f"{type(exc).__name__}: {exc}"
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            message += f" | Context: {context_str}"

        self.logger.error(message)


wlogger = WRedisLogger()

try:
    raise OperationError("SET failed")
except WRedisError as exc:
    wlogger.log_error(exc, context={"key": "user:1", "operation": "SET"})

try:
    raise RedisConnectionError("Timeout after 30s")
except WRedisError as exc:
    wlogger.log_error(exc, context={"host": "localhost", "port": 6379})
