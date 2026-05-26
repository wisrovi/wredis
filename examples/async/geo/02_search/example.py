import asyncio

from wredis.aio import RedisGeoManager


async def main():
    geo = RedisGeoManager(host="localhost")
    await geo.add_location("places", "store_a", -122.4194, 37.7749)
    await geo.add_location("places", "store_b", -122.4084, 37.7849)

    nearby = await geo.search_nearby("places", -122.4194, 37.7749, 1, unit="km")
    print(f"Nearby stores: {nearby}")


if __name__ == "__main__":
    asyncio.run(main())
