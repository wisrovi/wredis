import asyncio

from wredis.aio import RedisPubSubManager


async def main():
    manager = RedisPubSubManager(host="localhost")
    await manager.publish_message("channel_1", "Hello, Redis!")
    await manager.publish_message("channel_2", {"saludo": "Hola desde channel_2!"})


if __name__ == "__main__":
    asyncio.run(main())
