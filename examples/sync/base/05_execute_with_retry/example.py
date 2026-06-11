"""Example 05: Executing operations with automatic retries.

Demonstrates the _execute() method that executes Redis operations
with retry logic using exponential backoff.
"""

from wredis.sync import BaseManager

print("=== Execution with Retries (_execute) ===\n")

# Create the manager - it handles connection automatically
with BaseManager(verbose=False) as manager:
    # _execute allows executing any Redis client operation
    # with automatic retries in case of connection failures
    print("Executing operations with _execute():")

    # SET operation with retries
    result_set = manager._execute("set", "retry:key", "value_with_retry")
    print(f"  SET executed: {result_set}")

    # GET operation with retries
    result_get = manager._execute("get", "retry:key")
    print(f"  GET executed: {result_get}")

    # INCR operation with retries
    manager._execute("set", "retry:counter", "0")
    result_incr = manager._execute("incr", "retry:counter")
    print(f"  INCR executed: {result_incr}")

    # HSET operation with retries
    result_hset = manager._execute("hset", "retry:hash", mapping={"field1": "value1", "field2": "value2"})
    print(f"  HSET executed: {result_hset} fields")

    # HGETALL operation with retries
    result_hgetall = manager._execute("hgetall", "retry:hash")
    print(f"  HGETALL executed: {result_hgetall}")

print("\nAll operations executed with automatic retries")
