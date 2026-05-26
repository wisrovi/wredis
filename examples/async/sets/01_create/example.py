import asyncio

from wredis.aio import RedisSetManager


async def main():
    manager = RedisSetManager(host="localhost")
    await manager.add_to_set("my_set", "value1", "value2", "value3")
    await manager.add_to_set("my_set", "value4", ttl=60)


if __name__ == "__main__":
    asyncio.run(main())
