import asyncio

from wredis.aio import RedisTransactionManager


async def main():
    txn = RedisTransactionManager(host="localhost")
    results = await txn.execute_transaction(
        [
            ("set", ["balance:alice", "100"]),
            ("incrby", ["balance:alice", 50]),
            ("get", ["balance:alice"]),
        ]
    )
    print(f"Transaction results: {results}")


if __name__ == "__main__":
    asyncio.run(main())
