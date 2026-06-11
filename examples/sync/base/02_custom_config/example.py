"""Example 02: Custom BaseManager configuration.

Demonstrates how to initialize BaseManager with custom parameters
such as host, port, database, timeout, and maximum connections.
"""

from wredis.sync import BaseManager

# Custom configuration for a production environment
manager = BaseManager(
    host="localhost",
    port=6379,
    db=0,
    socket_timeout=10.0,
    max_connections=20,
    decode_responses=True,
    verbose=False,
)

# Display the applied configuration
print("BaseManager custom configuration:")
print("  Host: localhost")
print("  Port: 6379")
print("  Database: 0")
print("  Socket timeout: 10.0s")
print("  Max connections: 20")
print("  Decode responses: True")
print(f"  Verbose: {manager.verbose}")

# Verify it works with the configuration
manager._execute("set", "config:environment", "production")
value = manager._execute("get", "config:environment")
print(f"\nWrite/read test: {value}")

manager.close()
print("Connection closed successfully")
