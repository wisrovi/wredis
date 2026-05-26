"""14 - Async rate limiter

This example implements a rate limiter using Redis with the
sliding window log algorithm, leveraging BaseManager's
async operations.
"""

import asyncio
import time
from typing import Any

from wredis.aio import BaseManager


class RateLimiter:
    def __init__(self, manager: BaseManager, max_requests: int, window_seconds: int):
        self.manager = manager
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def is_allowed(self, client_id: str) -> tuple[bool, dict[str, Any]]:
        key = f"ratelimit:{client_id}"
        now = time.time()
        window_start = now - self.window_seconds

        await self.manager._execute("zremrangebyscore", key, 0, window_start)

        count = await self.manager._execute("zcard", key)

        if count < self.max_requests:
            await self.manager._execute("zadd", key, {str(now): now})
            await self.manager._execute("expire", key, self.window_seconds)
            return True, {
                "allowed": True,
                "requests_used": count + 1,
                "requests_remaining": self.max_requests - count - 1,
                "window_seconds": self.window_seconds,
            }
        else:
            return False, {
                "allowed": False,
                "requests_used": count,
                "requests_remaining": 0,
                "window_seconds": self.window_seconds,
            }


async def main():
    async with BaseManager(verbose=False) as manager:
        limiter = RateLimiter(manager, max_requests=5, window_seconds=10)

        print("=== Rate Limiter - 5 requests / 10 seconds ===\n")

        rate_limit_client = "user_123"
        for i in range(8):
            allowed, info = await limiter.is_allowed(rate_limit_client)
            status = "ALLOWED" if allowed else "DENIED"
            print(
                f"  Request {i + 1}: {status} | "
                f"Used: {info['requests_used']}/{5} | "
                f"Remaining: {info['requests_remaining']}"
            )

        print("\n=== State in Redis ===")
        key = f"ratelimit:{rate_limit_client}"
        entries = await manager._execute("zrange", key, 0, -1, "WITHSCORES")
        print(f"  Entries in sorted set: {len(entries) // 2}")
        ttl = await manager._execute("ttl", key)
        print(f"  Remaining TTL: {ttl}s")

        print("\n=== Another client (independent limit) ===")
        client_id_2 = "user_456"
        allowed, info = await limiter.is_allowed(client_id_2)
        status = "ALLOWED" if allowed else "DENIED"
        print(f"  Request 1 of user_456: {status}")

    print("\nRate Limiter completed")


if __name__ == "__main__":
    asyncio.run(main())
