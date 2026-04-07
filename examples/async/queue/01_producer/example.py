import asyncio

from wredis.aio import RedisQueueManager


async def main():
    manager = RedisQueueManager(host="localhost")
    await manager.publish("tasks", {"task_id": 1, "description": "Process order"})
    await manager.publish("tasks", {"task_id": 2, "description": "Send email"}, ttl=60)
    await manager.publish("priority", {"task_id": 3, "priority": "high"})
    await manager.close()


if __name__ == "__main__":
    asyncio.run(main())
