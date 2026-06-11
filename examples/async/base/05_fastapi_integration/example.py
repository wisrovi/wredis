"""05 - FastAPI integration

This example shows how to integrate BaseManager with FastAPI
to create endpoints that interact with Redis asynchronously.
Uses a startup/shutdown lifecycle to manage the connection.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict

from wredis.aio import BaseManager

redis_manager: BaseManager | None = None


@asynccontextmanager
async def lifespan(app: dict[str, Any]):
    global redis_manager
    redis_manager = BaseManager(verbose=False)
    connected = await redis_manager.health_check()
    print(f"FastAPI startup - Redis connected: {connected}")
    yield
    if redis_manager:
        await redis_manager.close()
        print("FastAPI shutdown - Redis disconnected")


async def simulate_fastapi():
    global redis_manager

    app = {"name": "my_api"}

    async with lifespan(app):
        print("\n--- GET /health ---")
        status = await redis_manager.health_check()
        print(f'{{"status": "healthy", "redis": {status}}}')

        print("\n--- POST /cache ---")
        await redis_manager._execute("set", "cache:page:home", "HTML content")
        print('{"action": "cached", "key": "cache:page:home"}')

        print("\n--- GET /cache/cache:page:home ---")
        content = await redis_manager._execute("get", "cache:page:home")
        print(f'{{"key": "cache:page:home", "value": "{content}"}}')

        print("\n--- DELETE /cache/cache:page:home ---")
        await redis_manager._execute("delete", "cache:page:home")
        print('{"action": "deleted", "key": "cache:page:home"}')

    print("\nSimulated FastAPI completed")


async def main():
    await simulate_fastapi()


if __name__ == "__main__":
    asyncio.run(main())
