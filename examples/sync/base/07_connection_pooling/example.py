"""Example 07: Connection pool management.

Demonstrates how BaseManager internally handles a connection pool
and how the maximum number of connections can be configured.
"""

from wredis.sync import BaseManager

print("=== Connection Pool Management ===\n")

# Create a manager with a configured connection pool
manager = BaseManager(
    max_connections=5,
    decode_responses=True,
    verbose=False,
)

# Connection pool is created automatically
print(f"Connection pool created: {type(manager._pool).__name__}")
print(f"Maximum connections configured: {manager._pool.max_connections}")

# Verify that operations work with the pool
print("\nExecuting operations with the connection pool:")

# Multiple operations that would use the pool in a real environment
for i in range(3):
    manager._execute("set", f"pool:key:{i}", f"value_{i}")
    value = manager._execute("get", f"pool:key:{i}")
    print(f"  Operation {i + 1}: SET/GET of pool:key:{i} = {value}")

# Pool information
print(f"\nPool status:")
print(f"  Pool type: {type(manager._pool).__name__}")
print(f"  Max connections: {manager._pool.max_connections}")

# Close the pool explicitly
manager.close()
print("\nConnection pool closed successfully")
