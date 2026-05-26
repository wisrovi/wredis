import asyncio

from wredis.aio import RedisGeoManager


async def main():
    geo = RedisGeoManager(host="localhost")
    await geo.add_location("cities", "new_york", -74.006, 40.7128)
    await geo.add_location("cities", "los_angeles", -118.2437, 34.0522)

    distance = await geo.get_distance("cities", "new_york", "los_angeles", unit="km")
    print(f"Distance: {distance} km")


if __name__ == "__main__":
    asyncio.run(main())
