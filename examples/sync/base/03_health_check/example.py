"""Example 03: Health check verification.

Demonstrates the use of the health_check() method to verify that the
connection to Redis is active and working correctly.
"""

from wredis.sync import BaseManager

# Create the manager - it handles connection automatically
manager = BaseManager(verbose=False)

# Check the connection status
print("=== Health Check Verification ===\n")

# health_check() returns True if the connection is active
status = manager.health_check()
print(f"Connection status: {'ACTIVE' if status else 'INACTIVE'}")

# Simulate an operation to confirm everything works
manager._execute("set", "health:check", "ok")
value = manager._execute("get", "health:check")
print(f"Operation test: {value}")

# health_check uses PING internally
ping_result = manager.redis_client.ping()
print(f"PING result: {ping_result}")

manager.close()
print("\nConnection closed successfully")
