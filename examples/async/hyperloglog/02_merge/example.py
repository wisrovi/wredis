import asyncio

from wredis.aio import RedisHyperLogLogManager


async def main():
    hll = RedisHyperLogLogManager(host="localhost")
    await hll.add("day1", "user1", "user2", "user3")
    await hll.add("day2", "user3", "user4", "user5")
    await hll.add("day3", "user1", "user5", "user6")

    await hll.merge("total", "day1", "day2", "day3")

    total = await hll.count("total")
    print(f"Total unique: {total}")


if __name__ == "__main__":
    asyncio.run(main())
