"""Example 12: Verbose mode and its impact on logging.

Demonstrates the difference between running BaseManager with verbose=True
and verbose=False, and how it affects operation logging.
"""

from wredis.sync import BaseManager

print("=== Verbose vs Silent Mode ===\n")

print("--- Scenario 1: verbose=True ---")
verbose_manager = BaseManager(verbose=True)

print(f"Verbose status: {verbose_manager.verbose}")
verbose_manager.log("Operation started", level="info")
verbose_manager._execute("set", "verbose:key", "test_data")
verbose_manager.log("Data stored", level="info")
value = verbose_manager._execute("get", "verbose:key")
print(f"Value retrieved: {value}")

print("\n--- Scenario 2: verbose=False ---")
silent_manager = BaseManager(verbose=False)

print(f"Verbose status: {silent_manager.verbose}")
silent_manager.log("This operation is NOT logged", level="info")
silent_manager._execute("set", "silent:key", "test_data")
silent_manager.log("Data stored (without logging)", level="info")
value = silent_manager._execute("get", "silent:key")
print(f"Value retrieved: {value}")
print("(The previous log messages did not appear)")

print("\n--- Scenario 3: Dynamic verbose switching ---")
dynamic_manager = BaseManager(verbose=False)

print(f"Initial verbose: {dynamic_manager.verbose}")
dynamic_manager.log("Message 1 (does not appear)", level="info")

dynamic_manager.verbose = True
print(f"Verbose after change: {dynamic_manager.verbose}")
dynamic_manager.log("Message 2 (appears)", level="info")

dynamic_manager.verbose = False
print(f"Verbose after second change: {dynamic_manager.verbose}")
dynamic_manager.log("Message 3 (does not appear)", level="info")

verbose_manager.close()
silent_manager.close()
dynamic_manager.close()
print("\nAll connections closed successfully")
