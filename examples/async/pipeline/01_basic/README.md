# Pipeline - Basic

## Description
Demonstrates executing multiple Redis commands in a pipeline. Reduces network round-trips by batching commands.

## Code

```python
import asyncio
from wredis.async_api import AsyncRedisPipelineManager


async def main():
    pipeline = AsyncRedisPipelineManager(host="localhost")
    results = await pipeline.execute_commands(
        [
            ("set", ["key1", "value1"]),
            ("set", ["key2", "value2"]),
            ("get", ["key1"]),
            ("get", ["key2"]),
        ]
    )
    print(f"Results: {results}")


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
    A[Async Function] --> B[AsyncRedisPipelineManager]
    B --> C[Redis Pipeline]
```