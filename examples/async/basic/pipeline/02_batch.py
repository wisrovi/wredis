import asyncio
from wredis.async_api import AsyncRedisPipelineManager


async def main():
    pipeline = AsyncRedisPipelineManager(host="localhost")
    mapping = {
        "user:1": '{"name": "Alice"}',
        "user:2": '{"name": "Bob"}',
    }
    await pipeline.mset_pipeline(mapping)

    values = await pipeline.mget_pipeline("user:1", "user:2")
    print(f"Values: {values}")


if __name__ == "__main__":
    asyncio.run(main())
