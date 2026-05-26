# HyperLogLog - Basic

## Description
Demonstrates using Redis HyperLogLog for efficient probabilistic counting of unique elements. Memory-efficient for large datasets.

## Code

```python
import asyncio
from wredis.async_api import AsyncRedisHyperLogLogManager


async def main():
    hll = AsyncRedisHyperLogLogManager(host="localhost")
    await hll.add("visitors", "user1", "user2", "user3", "user4", "user5")

    count = await hll.count("visitors")
    print(f"Unique visitors: {count}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Run

```bash
python example.py
```

## Diagram

```mermaid
graph LR
    A[Async Function] --> B[AsyncRedisHyperLogLogManager]
    B --> C[Redis HyperLogLog]
```