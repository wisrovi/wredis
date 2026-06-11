# 14 Pipeline Operations

Quickly understand if this example fits your needs.

```mermaid
graph LR
    A[Commands] --> B[Pipeline]
    B --> C[Batched execution]
    C --> D[Redis Server]
```

## What it does

Demonstrates how to use Redis pipelines together with BaseManager to execute multiple operations atomically and efficiently.

## When to use it

- High-performance bulk operations
- Atomic multi-command transactions
- Reducing network round-trips

## Code

```python
# Copy and adapt to your needs
import redis
from wredis._base import BaseManager

print("=== Pipeline Operations ===\n")

with BaseManager(verbose=False) as manager:
    manager.redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    # Pipeline 1: Bulk write operations
    print("1. Bulk write pipeline:")
    pipe = manager.redis_client.pipeline()
    for i in range(5):
        pipe.set(f"pipeline:key:{i}", f"value_{i}")
    results = pipe.execute()
    print(f"   {len(results)} SET operations executed in pipeline")
    print(f"   Results: {results}")

    # Verify the data was stored
    for i in range(5):
        value = manager._execute("get", f"pipeline:key:{i}")
        print(f"   pipeline:key:{i} = {value}")

    # Pipeline 2: Mixed operations
    print("\n2. Mixed operations pipeline:")
    pipe = manager.redis_client.pipeline()
    pipe.set("pipeline:user:name", "Ana Garcia")
    pipe.set("pipeline:user:email", "ana@example.com")
    pipe.set("pipeline:user:role", "administrator")
    pipe.incr("pipeline:user:count")
    results = pipe.execute()
    print(f"   {len(results)} mixed operations executed")

    # Verify the data
    name = manager._execute("get", "pipeline:user:name")
    email = manager._execute("get", "pipeline:user:email")
    role = manager._execute("get", "pipeline:user:role")
    count = manager._execute("get", "pipeline:user:count")
    print(f"   Name: {name}")
    print(f"   Email: {email}")
    print(f"   Role: {role}")
    print(f"   User count: {count}")

    # Pipeline 3: Read operations
    print("\n3. Read operations pipeline:")
    pipe = manager.redis_client.pipeline()
    for i in range(5):
        pipe.get(f"pipeline:key:{i}")
    results = pipe.execute()
    print(f"   {len(results)} values read in pipeline")
    print(f"   Values: {results}")

    # Pipeline 4: Hash operations
    print("\n4. Pipeline with hashes:")
    pipe = manager.redis_client.pipeline()
    pipe.hset("pipeline:product:1", mapping={"name": "Laptop", "price": "999.99"})
    pipe.hset("pipeline:product:2", mapping={"name": "Mouse", "price": "29.99"})
    pipe.hgetall("pipeline:product:1")
    pipe.hgetall("pipeline:product:2")
    results = pipe.execute()
    print(f"   {len(results)} hash operations")
    print(f"   Product 1: {results[2]}")
    print(f"   Product 2: {results[3]}")

print("\nAll pipelines executed successfully")
```

## Run it

```bash
python example.py
```

## Expected output

```
=== Pipeline Operations ===

1. Bulk write pipeline:
   5 SET operations executed in pipeline
   Results: [True, True, True, True, True]
   pipeline:key:0 = value_0
   pipeline:key:1 = value_1
   pipeline:key:2 = value_2
   pipeline:key:3 = value_3
   pipeline:key:4 = value_4

2. Mixed operations pipeline:
   4 mixed operations executed
   Name: Ana Garcia
   Email: ana@example.com
   Role: administrator
   User count: 1

3. Read operations pipeline:
   5 values read in pipeline
   Values: ['value_0', 'value_1', 'value_2', 'value_3', 'value_4']

4. Pipeline with hashes:
   4 hash operations
   Product 1: {'name': 'Laptop', 'price': '999.99'}
   Product 2: {'name': 'Mouse', 'price': '29.99'}

All pipelines executed successfully
```
