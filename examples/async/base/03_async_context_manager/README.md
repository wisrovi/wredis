# 03 Async Context Manager

Quickly understand if this example fits your needs.

```mermaid
graph LR
    A[Client] --> B[async with]
    B --> C[AsyncBaseManager]
    C --> D[Redis]
    D --> E[Auto-close]
```

## What it does

Shows how to use `AsyncBaseManager` as an async context manager with `async with`, which guarantees automatic connection cleanup when exiting the block.

## When to use it

- Automatic lifecycle management
- Ensuring connections are properly closed
- Clean resource management

## Code

```python
# Copy and adapt to your needs
"""03 - Async context manager usage

This example shows how to use AsyncBaseManager as an async context
manager with 'async with', which guarantees that the connection is
automatically closed when exiting the block.
"""

import asyncio

import redis.asyncio
from wredis._async_base import AsyncBaseManager


async def main():
    # Create a real Redis client
    client = redis.asyncio.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    # Use 'async with' for automatic lifecycle management
    # The connection opens on entry and closes on exit from the block
    async with AsyncBaseManager(verbose=True) as manager:
        # Inject the Redis client
        manager.redis_client = client

        # Verify connection within context
        connected = await manager.health_check()
        print(f"Inside context - Connected: {connected}")

        # Perform several operations safely
        await manager._execute("set", "key1", "value1")
        await manager._execute("set", "key2", "value2")

        value1 = await manager._execute("get", "key1")
        value2 = await manager._execute("get", "key2")
        print(f"key1 = {value1}, key2 = {value2}")

    # Outside the context, the connection is already closed
    await client.aclose()
    print("Outside context - connection closed automatically")


if __name__ == "__main__":
    asyncio.run(main())
```

## Run it

```bash
python example.py
```

## Expected output

```
Inside context - Connected: True
key1 = value1, key2 = value2
Outside context - connection closed automatically
```
