"""Example 04: Using BaseManager as a context manager.

Demonstrates how to use BaseManager with the 'with' statement to
ensure that resources are automatically released when exiting the block.
"""

from wredis.sync import BaseManager

print("=== Context Manager ===\n")

# Use BaseManager as a context manager with 'with'
# This ensures that close() is called automatically when exiting the block
with BaseManager(verbose=False) as manager:
    # Verify the connection works within the context
    print(f"Inside context - Client: {type(manager.redis_client).__name__}")

    # Perform operations within the context
    manager._execute("set", "context:key", "context_value")
    result = manager._execute("get", "context:key")
    print(f"Value within context: {result}")

    # Check health
    print(f"Health check within context: {manager.health_check()}")

# When exiting the 'with' block, manager.close() is called automatically
print("\nOutside context - resources were automatically released")
print("Connection closed successfully")
