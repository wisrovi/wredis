"""11 - Multiple databases

This example demonstrates how to connect and operate on multiple
Redis databases (db=0, db=1, db=2) using separate instances
of BaseManager.
"""

import asyncio

from wredis.aio import BaseManager


async def main():
    db_cache = BaseManager(db=0, decode_responses=True, verbose=False)
    db_sessions = BaseManager(db=1, decode_responses=True, verbose=False)
    db_temp = BaseManager(db=2, decode_responses=True, verbose=False)

    try:
        print("=== Verifying connections ===")
        for name, mgr in [
            ("Cache (db=0)", db_cache),
            ("Sessions (db=1)", db_sessions),
            ("Temp (db=2)", db_temp),
        ]:
            status = await mgr.health_check()
            print(f"  {name}: {status}")

        print("\n=== Writing to db=0 (Cache) ===")
        await db_cache._execute("set", "cache:page:home", "<html>...</html>")
        await db_cache._execute("set", "cache:page:about", "<html>about</html>")
        value = await db_cache._execute("get", "cache:page:home")
        print(f"  cache:page:home = {value}")

        print("\n=== Writing to db=1 (Sessions) ===")
        await db_sessions._execute("set", "session:abc123", '{"user": "admin"}')
        await db_sessions._execute("set", "session:def456", '{"user": "editor"}')
        value = await db_sessions._execute("get", "session:abc123")
        print(f"  session:abc123 = {value}")

        print("\n=== Writing to db=2 (Temp) ===")
        await db_temp._execute("set", "temp:job:001", "processing", ex=60)
        await db_temp._execute("set", "temp:job:002", "pending", ex=120)
        value = await db_temp._execute("get", "temp:job:001")
        ttl = await db_temp._execute("ttl", "temp:job:001")
        print(f"  temp:job:001 = {value} (TTL: {ttl}s)")

        print("\n=== Verifying isolation ===")
        data_in_db0 = await db_cache._execute("get", "session:abc123")
        data_in_db1 = await db_sessions._execute("get", "cache:page:home")
        print(f"  session:abc123 in db=0: {data_in_db0} (should be None)")
        print(f"  cache:page:home in db=1: {data_in_db1} (should be None)")

    finally:
        await db_cache.close()
        await db_sessions.close()
        await db_temp.close()
        print("\nAll connections closed")


if __name__ == "__main__":
    asyncio.run(main())
