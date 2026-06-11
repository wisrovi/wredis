# 07 Connection Pooling

Quickly understand if this example fits your needs.

```mermaid
graph LR
    A[Client] --> B[Pool Manager]
    B --> C[Pool: 20 connections]
    C --> D[Redis]
```

## What it does

Shows how to configure the Redis connection pool with custom parameters like `max_connections`, `socket_timeout` and `decode_responses` to optimize performance.

## When to use it

- High-throughput applications
- Connection reuse optimization
- Timeout configuration for slow operations

## Code

```python
# Copy and adapt to your needs
"""07 - Connection pool configuration

This example shows how to configure the Redis connection pool
with custom parameters like max_connections, socket_timeout
and decode_responses to optimize performance.
"""

import asyncio

import redis.asyncio
from wredis._async_base import AsyncBaseManager


async def main():
    # Create a real Redis client
    client = redis.asyncio.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    # Configure a connection pool with custom parameters
    manager = AsyncBaseManager(
        decode_responses=True,  # Responses are returned as str instead of bytes
        socket_timeout=10.0,  # 10 second timeout for slow operations
        max_connections=20,  # Pool of up to 20 simultaneous connections
        verbose=True,
    )
    # Inject the Redis client
    manager.redis_client = client

    # Verify connection
    connected = await manager.health_check()
    print(f"Connection established: {connected}")

    # The connection pool allows reusing existing connections
    # This is more efficient than creating a new connection per operation
    for i in range(5):
        await manager._execute("set", f"pool:key:{i}", f"value_{i}")
        print(f"  Set pool:key:{i} -> value_{i}")

    # Read all keys using the same pool
    print("\nReading keys from pool:")
    for i in range(5):
        value = await manager._execute("get", f"pool:key:{i}")
        print(f"  pool:key:{i} = {value}")

    # Show pool information
    print(f"\nMaximum pool size: 20 connections")
    print(f"Socket timeout: 10.0 seconds")
    print(f"Decode responses: True")

    await manager.close()
    await client.aclose()
    print("\nConnection pool closed")


if __name__ == "__main__":
    asyncio.run(main())
```

## Run it

```bash
python example.py
```

## Expected output

```
Connection established: True
  Set pool:key:0 -> value_0
  Set pool:key:1 -> value_1
  Set pool:key:2 -> value_2
  Set pool:key:3 -> value_3
  Set pool:key:4 -> value_4

Reading keys from pool:
  pool:key:0 = value_0
  pool:key:1 = value_1
  pool:key:2 = value_2
  pool:key:3 = value_3
  pool:key:4 = value_4

Maximum pool size: 20 connections
Socket timeout: 10.0 seconds
Decode responses: True

Connection pool closed
```
