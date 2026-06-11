import asyncio

from wredis.aio import RedisStreamManager


async def main():
    manager = RedisStreamManager(host="localhost")
    msg_id = await manager.add_to_stream("my_stream", {"event": "user_login", "user": "alice"})
    print(f"Message ID: {msg_id}")
    await manager.add_to_stream("my_stream", {"event": "user_logout", "user": "bob"})
    await manager.close()


if __name__ == "__main__":
    asyncio.run(main())
