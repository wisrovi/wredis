"""09 - Custom manager with inheritance

This example shows how to create a custom manager by inheriting
from BaseManager, adding specific methods for particular
use cases like user session management.
"""

import asyncio
import json
from typing import Any

from wredis.aio import BaseManager


class SessionManager(BaseManager):
    def __init__(self, session_ttl: int = 3600, **kwargs: Any):
        super().__init__(**kwargs)
        self.session_ttl = session_ttl
        self.prefix = "session"

    async def create_session(self, user_id: str, data: dict) -> str:
        session_key = f"{self.prefix}:{user_id}"
        await self._execute("set", session_key, json.dumps(data), ex=self.session_ttl)
        self.log(f"Session created for user {user_id}")
        return session_key

    async def get_session(self, user_id: str) -> dict | None:
        session_key = f"{self.prefix}:{user_id}"
        data = await self._execute("get", session_key)
        if data:
            return json.loads(data)
        return None

    async def delete_session(self, user_id: str) -> bool:
        session_key = f"{self.prefix}:{user_id}"
        deleted = await self._execute("delete", session_key)
        self.log(f"Session deleted for user {user_id}")
        return bool(deleted)

    async def refresh_session(self, user_id: str) -> bool:
        session_key = f"{self.prefix}:{user_id}"
        refreshed = await self._execute("expire", session_key, self.session_ttl)
        return bool(refreshed)


async def main():
    async with SessionManager(
        decode_responses=True,
        session_ttl=1800,
        verbose=True,
    ) as session_mgr:
        connected = await session_mgr.health_check()
        print(f"SessionManager connected: {connected}")

        print("\n=== Create session ===")
        user_data = {
            "name": "Carlos",
            "role": "admin",
            "last_activity": "2026-04-03T10:00:00",
        }
        key = await session_mgr.create_session("user_42", user_data)
        print(f"Session created: {key}")

        print("\n=== Get session ===")
        session = await session_mgr.get_session("user_42")
        print(f"Session data: {session}")

        print("\n=== Refresh session ===")
        refreshed = await session_mgr.refresh_session("user_42")
        print(f"Session refreshed: {refreshed}")

        print("\n=== Delete session ===")
        deleted = await session_mgr.delete_session("user_42")
        print(f"Session deleted: {deleted}")

        session = await session_mgr.get_session("user_42")
        print(f"Session after deletion: {session}")

    print("\nCustom manager completed")


if __name__ == "__main__":
    asyncio.run(main())
