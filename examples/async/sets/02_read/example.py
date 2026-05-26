import asyncio

from wredis.aio import RedisSetManager


async def main():
    manager = RedisSetManager(host="localhost")
    members = await manager.get_set_members("my_set")
    print(f"Members: {members}")


if __name__ == "__main__":
    asyncio.run(main())
