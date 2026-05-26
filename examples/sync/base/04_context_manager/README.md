# 04 Context Manager

Quickly understand if this example fits your needs.

```mermaid
graph LR
    A[with statement] --> B[BaseManager]
    B --> C[__enter__]
    C --> D[Operations]
    D --> E[__exit__]
    E --> F[close()]
```

## What it does

Demonstrates how to use BaseManager with the `with` statement to ensure that resources are automatically released when exiting the block.

## When to use it

- Ensuring proper resource cleanup
- Writing clean, Pythonic code
- Avoiding connection leaks

## Code

```python
# Copy and adapt to your needs
import redis
from wredis._base import BaseManager

print("=== Context Manager ===\n")

# Use BaseManager as a context manager
with BaseManager(verbose=False) as manager:
    # Configure a real Redis client
    manager.redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    # Verify connection works within context
    print(f"Inside context - Client: {type(manager.redis_client).__name__}")

    # Perform operations within context
    manager.redis_client.set("context:key", "context_value")
    result = manager.redis_client.get("context:key")
    print(f"Value within context: {result}")

    # Health check within context
    print(f"Health check within context: {manager.health_check()}")

# When exiting, close() is called automatically
print("\nOutside context - resources were automatically released")
print("Connection closed successfully")
```

## Run it

```bash
python example.py
```

## Expected output

```
=== Context Manager ===

Inside context - Client: Redis
Value within context: context_value
Health check within context: True

Outside context - resources were automatically released
Connection closed successfully
```