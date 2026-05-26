import asyncio

from wredis.aio import RedisSortedSetManager


async def main():
    manager = RedisSortedSetManager(host="localhost")
    await manager.add_to_sorted_set("leaderboard", 100, "player1")
    await manager.add_to_sorted_set("leaderboard", 200, "player2")
    await manager.add_to_sorted_set("leaderboard", 150, "player3", ttl=60)


if __name__ == "__main__":
    asyncio.run(main())
