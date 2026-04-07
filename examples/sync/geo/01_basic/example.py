from wredis.sync import RedisGeoManager

geo_manager = RedisGeoManager(host="localhost")

geo_manager.add_location("cities", "new_york", -74.006, 40.7128)
geo_manager.add_location("cities", "los_angeles", -118.2437, 34.0522)
geo_manager.add_location("cities", "chicago", -87.6298, 41.8781)

distance = geo_manager.get_distance("cities", "new_york", "los_angeles", unit="km")
print(f"Distance NY to LA: {distance} km")

positions = geo_manager.get_positions("cities", "new_york", "chicago")
print(f"Positions: {positions}")
