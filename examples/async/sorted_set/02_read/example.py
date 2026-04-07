import asyncio

from wredis.aio import RedisSortedSetManager


async def main():
    manager = RedisSortedSetManager(host="localhost")
    items = await manager.get_sorted_set("leaderboard", with_scores=True)
    print(f"Leaderboard: {items}")


if __name__ == "__main__":
    asyncio.run(main())
