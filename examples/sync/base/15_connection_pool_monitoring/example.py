"""Example 15: Connection pool monitoring.

Demonstrates how to monitor and get information about the status of
the Redis connection pool managed by BaseManager.
"""

from wredis.sync import BaseManager

print("=== Connection Pool Monitoring ===\n")

manager = BaseManager(
    max_connections=10,
    socket_timeout=5.0,
    verbose=False,
)

print("1. Pool information:")
print(f"   Type: {type(manager._pool).__name__}")
print(f"   Max connections: {manager._pool.max_connections}")
print(f"   Configured host: {manager._pool.connection_kwargs.get('host', 'localhost')}")
print(f"   Configured port: {manager._pool.connection_kwargs.get('port', 6379)}")
print(f"   Database: {manager._pool.connection_kwargs.get('db', 0)}")
print(f"   Timeout: {manager._pool.connection_kwargs.get('socket_timeout', 5.0)}s")

print("\n2. Monitoring during operations:")
for i in range(3):
    manager._execute("set", f"monitor:key:{i}", f"value_{i}")
    value = manager._execute("get", f"monitor:key:{i}")
    print(f"   Operation {i + 1}: {value}")

print("\n3. Pool status after operations:")
print(f"   Max connections: {manager._pool.max_connections}")

print("\n4. Redis client information:")
print(f"   Client type: {type(manager.redis_client).__name__}")
print(f"   Decode responses: {manager.redis_client.connection_pool.connection_kwargs.get('decode_responses', False)}")

print("\n5. Health check:")
status = manager.health_check()
print(f"   Status: {'ACTIVE' if status else 'INACTIVE'}")

print("\n6. Simulated metrics:")
metrics = {
    "max_connections": manager._pool.max_connections,
    "connection_status": "active" if manager.health_check() else "inactive",
    "socket_timeout": f"{manager._pool.connection_kwargs.get('socket_timeout', 5.0)}s",
    "successful_operations": 6,
    "failed_operations": 0,
}
for metric, value in metrics.items():
    print(f"   {metric}: {value}")

manager.close()
print("\n7. After closing:")
print("   Pool disconnected successfully")
print("   Monitoring completed")
