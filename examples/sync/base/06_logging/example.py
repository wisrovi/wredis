"""Example 06: Integrated logging system.

Demonstrates the log() method that allows logging messages with
different levels using loguru when verbose is enabled.
"""

from wredis.sync import BaseManager

print("=== Integrated Logging System ===\n")

# Create the manager with verbose=True to enable logging
manager = BaseManager(verbose=True)

# The log() method logs messages with different levels
# Supported levels are: debug, info, warning, error, critical
print("Logging messages with different levels:\n")

manager.log("Initializing test operations", level="info")
manager.log("This is a debug message", level="debug")
manager.log("Warning: slow operation detected", level="warning")

# Perform operations while logging events
manager.log("Executing SET", level="debug")
manager._execute("set", "log:key", "log_value")
manager.log("SET completed successfully", level="info")

manager.log("Executing GET", level="debug")
value = manager._execute("get", "log:key")
manager.log(f"GET completed - value: {value}", level="info")

# Create a manager with verbose=False to show it doesn't log
print("\n--- Manager with verbose=False (no logging) ---")
silent_manager = BaseManager(verbose=False)
silent_manager.log("This message will NOT appear", level="error")
print("The previous message was not logged because verbose=False")

manager.close()
silent_manager.close()
print("\nConnections closed successfully")
