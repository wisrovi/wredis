"""Using the serializer as a Redis storage simulation.

This example shows a common pattern where data is serialized
before being "stored" (simulated) and deserialized when
"retrieved", mimicking the actual flow with Redis.
"""

from wredis._serializer import deserialize, serialize

# Simulation of an in-memory Redis database
simulated_db = {}


def save_to_redis(key: str, value: dict) -> None:
    """Simulates saving a value to Redis by serializing it first."""
    serialized_data = serialize(value)
    simulated_db[key] = serialized_data
    print(f"  Saved '{key}': {len(serialized_data)} bytes")


def get_from_redis(key: str) -> dict:
    """Simulates getting a value from Redis by deserializing it."""
    serialized_data = simulated_db[key]
    return deserialize(serialized_data)


# Save several records
print("Saving records:")
save_to_redis(
    "user:1",
    {
        "name": "Maria Lopez",
        "email": "maria@example.com",
        "age": 30,
        "active": True,
    },
)
save_to_redis(
    "user:2",
    {
        "name": "Juan Perez",
        "email": "juan@example.com",
        "age": 25,
        "active": False,
    },
)
save_to_redis(
    "config:app",
    {
        "version": "2.1.0",
        "debug": False,
        "max_connections": 100,
    },
)

# Retrieve records
print("\nRetrieving records:")
user1 = get_from_redis("user:1")
print(f"  User 1: {user1}")

user2 = get_from_redis("user:2")
print(f"  User 2: {user2}")

config = get_from_redis("config:app")
print(f"  Configuration: {config}")

print(f"\nTotal keys stored: {len(simulated_db)}")
