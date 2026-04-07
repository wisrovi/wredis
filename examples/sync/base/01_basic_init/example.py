"""Example 01: Basic BaseManager initialization.

Demonstrates how to create a BaseManager instance with default
parameters and verify that the connection works.
"""

from wredis.sync import BaseManager

# Create an instance with default configuration
# Default values are: host=localhost, port=6379, db=0
# The manager handles the connection automatically
manager = BaseManager()

# Verify that the client is connected
print(f"Redis client created: {type(manager.redis_client).__name__}")
print(f"Verbose mode enabled: {manager.verbose}")

# Perform a basic operation to confirm it works
manager._execute("set", "example:01", "basic_initialization")
result = manager._execute("get", "example:01")
print(f"Value stored and retrieved: {result}")

# Clean up resources
manager.close()
print("Connection closed successfully")
