"""Generic catch with WRedisError as umbrella demonstration.

Shows how to catch any WRedis exception with a single
except block, useful when handling is indifferent to type.
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


def execute_risky_operation(operation_id):
    """Simulates operations that can throw different errors.

    Args:
        operation_id: Identifier that determines which error to raise.

    Raises:
        Various exceptions based on operation_id.
    """
    errors = {
        1: RedisConnectionError("Redis not responding"),
        2: SerializationError("Cannot serialize object"),
        3: CacheError("Failed to write to cache"),
        4: ValidationError("Field 'age' must be positive"),
        5: OperationError("SET operation failed"),
        6: TransactionError("WATCH transaction conflict"),
        7: QueueError("Queue full"),
        8: StreamError("Corrupted stream"),
        9: PubSubError("Channel not found"),
        10: SentinelError("Sentinel unavailable"),
        11: ClusterError("Cluster node down"),
    }
    raise errors.get(operation_id, WRedisError("Unknown error"))


# Catch all WRedis exceptions with a single block
print("=== Generic catch with WRedisError ===\n")

for op_id in range(1, 12):
    try:
        execute_risky_operation(op_id)
    except WRedisError as exc:
        # One block catches ALL wredis exceptions
        print(f"Operation {op_id:2d} | {type(exc).__name__:25s} | {exc}")

# Differentiate between WRedis errors and other errors
print("\n=== Differentiate WRedisError from other exceptions ===\n")


def mixed_operation(fails_with_wredis=True):
    """Simulates an operation that can fail in different ways."""
    if fails_with_wredis:
        raise CacheError("Cache unavailable")
    raise ValueError("Error unrelated to WRedis")


for fails_wredis in [True, False]:
    try:
        mixed_operation(fails_wredis)
    except WRedisError as exc:
        print(f"WRedis Error: {type(exc).__name__} - {exc}")
    except Exception as exc:
        print(f"External Error: {type(exc).__name__} - {exc}")
