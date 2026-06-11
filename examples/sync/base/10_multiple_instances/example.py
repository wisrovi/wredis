"""Example 10: Multiple BaseManager instances.

Demonstrates how to create and manage multiple independent
BaseManager instances connected to different databases.
"""

from wredis.sync import BaseManager

print("=== Multiple BaseManager Instances ===\n")

session_manager = BaseManager(db=0, verbose=False)
cache_manager = BaseManager(db=1, verbose=False)
queue_manager = BaseManager(db=2, verbose=False)

print("Instances created:")
print(f"  Sessions (db=0): {type(session_manager.redis_client).__name__}")
print(f"  Cache (db=1): {type(cache_manager.redis_client).__name__}")
print(f"  Queue (db=2): {type(queue_manager.redis_client).__name__}")

print("\nOperations on each instance:")

session_manager._execute("set", "session:user:1", "token_abc123")
session = session_manager._execute("get", "session:user:1")
print(f"  Session - user:1 = {session}")

cache_manager._execute("set", "cache:page:home", "<html>content</html>")
cache = cache_manager._execute("get", "cache:page:home")
print(f"  Cache - page:home = {cache[:30]}...")

queue_manager._execute("rpush", "queue:tasks", "send_email")
queue_manager._execute("rpush", "queue:tasks", "generate_report")
task = queue_manager._execute("lpop", "queue:tasks")
print(f"  Queue - task processed = {task}")

print("\nVerifying independence:")
print(f"  Session can see cache data: {session_manager._execute('get', 'cache:page:home')}")
print("  (Redis databases are independent)")

session_manager.close()
cache_manager.close()
queue_manager.close()
print("\nAll instances closed successfully")
