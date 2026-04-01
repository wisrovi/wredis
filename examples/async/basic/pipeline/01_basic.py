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
