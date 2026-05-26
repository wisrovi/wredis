"""15 - Complete FastAPI integration (advanced)

This example shows a more complete integration with FastAPI,
including rate limiting middleware, response caching and
session management, all managed by BaseManager.
"""

import asyncio
import json
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

from wredis.aio import BaseManager

redis_manager: BaseManager | None = None


class SimulatedRequest:
    def __init__(self, method: str, path: str, client_ip: str):
        self.method = method
        self.path = path
        self.client_ip = client_ip


async def rate_limit_middleware(request: SimulatedRequest) -> dict | None:
    global redis_manager
    if redis_manager is None:
        return None

    key = f"ratelimit:{request.client_ip}"
    now = time.time()
    window = 60
    max_req = 10

    await redis_manager._execute("zremrangebyscore", key, 0, now - window)
    count = await redis_manager._execute("zcard", key)

    if count >= max_req:
        return {"status": 429, "body": {"error": "Too many requests"}}

    await redis_manager._execute("zadd", key, {str(now): now})
    await redis_manager._execute("expire", key, window)
    return None


async def cache_middleware(request: SimulatedRequest) -> dict | None:
    global redis_manager
    if redis_manager is None or request.method != "GET":
        return None

    cache_key = f"cache:{request.method}:{request.path}"
    cached = await redis_manager._execute("get", cache_key)
    if cached:
        return {"status": 200, "body": json.loads(cached), "cached": True}
    return None


async def store_cache(request: SimulatedRequest, response: dict):
    global redis_manager
    if redis_manager is None or request.method != "GET":
        return

    cache_key = f"cache:{request.method}:{request.path}"
    await redis_manager._execute("set", cache_key, json.dumps(response), ex=120)


async def handle_request(request: SimulatedRequest) -> dict:
    rate_limit_response = await rate_limit_middleware(request)
    if rate_limit_response:
        return rate_limit_response

    cached_response = await cache_middleware(request)
    if cached_response:
        return cached_response

    response_data = {
        "path": request.path,
        "timestamp": time.time(),
        "data": f"Content of {request.path}",
    }

    await store_cache(request, response_data)

    return {"status": 200, "body": response_data, "cached": False}


@asynccontextmanager
async def app_lifespan():
    global redis_manager
    redis_manager = BaseManager(verbose=False)
    connected = await redis_manager.health_check()
    print(f"App startup - Redis: {'connected' if connected else 'failed'}")
    yield
    if redis_manager:
        await redis_manager.close()
        print("App shutdown - Redis disconnected")


async def main():
    async with app_lifespan():
        requests = [
            SimulatedRequest("GET", "/api/users", "192.168.1.100"),
            SimulatedRequest("GET", "/api/users", "192.168.1.100"),
            SimulatedRequest("POST", "/api/users", "192.168.1.100"),
            SimulatedRequest("GET", "/api/products", "192.168.1.200"),
            SimulatedRequest("GET", "/api/products", "192.168.1.200"),
        ]

        for i, req in enumerate(requests, 1):
            print(f"\n=== Request {i}: {req.method} {req.path} ({req.client_ip}) ===")
            response = await handle_request(req)

            if response.get("cached"):
                print(f"  [CACHE] Response from cache")
            else:
                print(f"  [NEW] Response generated")

            print(f"  Status: {response['status']}")
            body = response.get("body", {})
            if "error" in body:
                print(f"  Error: {body['error']}")
            elif "data" in body:
                print(f"  Data: {body['data']}")

        print("\n=== Redis state ===")
        keys = await redis_manager._execute("keys", "*")
        print(f"  Active keys: {len(keys)}")
        for key in sorted(keys):
            ttl = await redis_manager._execute("ttl", key)
            print(f"    {key} (TTL: {ttl}s)")

    print("\nAdvanced FastAPI integration completed")


if __name__ == "__main__":
    asyncio.run(main())
