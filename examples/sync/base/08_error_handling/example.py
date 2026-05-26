"""Example 08: Error handling with BaseManager.

Demonstrates how to handle connection errors and failed operations
using wredis custom exceptions.
"""

from wredis._exceptions import OperationError
from wredis.sync import BaseManager

print("=== Error Handling ===\n")

# Create the manager - it handles connection automatically
manager = BaseManager(verbose=False)

# Scenario 1: Successful operation
print("1. Successful operation:")
try:
    result = manager._execute("set", "error:key", "value")
    print(f"   SET successful: {result}")
except OperationError as e:
    print(f"   Unexpected error: {e}")

# Scenario 2: Successful health check
print("\n2. Successful health check:")
try:
    status = manager.health_check()
    print(f"   Connection active: {status}")
except OperationError as e:
    print(f"   Health check failed: {e}")

# Scenario 3: Operation with invalid data
print("\n3. Structured error handling:")
try:
    # Try an operation that might fail
    manager._execute("get", "nonexistent_key")
    print("   GET on nonexistent key: None (expected behavior)")
except OperationError as e:
    print(f"   Operation error: {e}")

# Scenario 4: Safe closing
print("\n4. Safe connection closing:")
try:
    manager.close()
    print("   Connection closed without errors")
except Exception as e:
    print(f"   Error closing: {e}")

# Scenario 5: Using context manager for automatic error handling
print("\n5. Context manager for automatic handling:")
try:
    with BaseManager(verbose=False) as m:
        m._execute("set", "context:error", "safe")
        print("   Operation within context: successful")
    print("   Resources automatically released when exiting context")
except OperationError as e:
    print(f"   Error caught: {e}")

print("\nAll error handling scenarios completed")
