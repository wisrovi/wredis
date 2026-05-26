"""Example 14: Pipeline operations with BaseManager.

Demonstrates how to use Redis pipelines together with BaseManager
to execute multiple operations atomically and efficiently.
"""

from wredis.sync import BaseManager

print("=== Pipeline Operations ===\n")

with BaseManager(verbose=False) as manager:
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
