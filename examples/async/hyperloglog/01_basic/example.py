import asyncio

from wredis.aio import RedisHyperLogLogManager


async def main():
    hll = RedisHyperLogLogManager(host="localhost")
    await hll.add("visitors", "user1", "user2", "user3", "user4", "user5")

    count = await hll.count("visitors")
    print(f"Unique visitors: {count}")


if __name__ == "__main__":
    asyncio.run(main())
