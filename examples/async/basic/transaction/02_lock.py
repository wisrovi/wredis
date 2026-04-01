import asyncio
from wredis.async_api import AsyncRedisTransactionManager


async def main():
    txn = AsyncRedisTransactionManager(host="localhost")

    set_result = await txn.set_if_not_exists("lock:process_1", "locked", ttl=60)
    print(f"Lock acquired: {set_result}")

    set_result_2 = await txn.set_if_not_exists("lock:process_1", "locked_again", ttl=60)
    print(f"Second lock: {set_result_2}")

    await txn.redis_client.delete("lock:process_1")

    set_result_3 = await txn.set_if_not_exists("lock:process_1", "locked", ttl=60)
    print(f"After delete, lock: {set_result_3}")


if __name__ == "__main__":
    asyncio.run(main())
