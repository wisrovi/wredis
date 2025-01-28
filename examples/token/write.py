from wredis.token import RedisTokenManager


# Create a RedisTokenManager instance with verbose logging enabled
redis_manager = RedisTokenManager(host="localhost", port=6379, db=0, verbose=True)

# Write data to Redis
token = "example_token"
data = {"name": "Alice", "age": 28, "city": "Paris"}
ttl = 120  # Set time-to-live to 120 seconds

if redis_manager.write_token(token, data, ttl=ttl):
    print(f"Token '{token}' written successfully.")
else:
    print(f"Failed to write token '{token}'.")
