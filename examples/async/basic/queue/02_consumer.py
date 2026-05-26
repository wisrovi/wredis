import asyncio

from wredis.aio import RedisQueueManager

manager = RedisQueueManager(poll_interval=2, host="localhost", verbose=False)


@manager.on_message("tasks")
async def worker_tasks(record):
    print(f"Processing tasks: {record}")


@manager.on_message("priority")
async def worker_priority(record):
    print(f"Processing priority: {record}")


async def main():
    await manager.start()
    await manager.wait()


if __name__ == "__main__":
    asyncio.run(main())
