from wredis.token import RedisTokenManager


# Create a RedisTokenManager instance with verbose logging disabled
redis_manager = RedisTokenManager(host="localhost", port=6379, db=0, verbose=False)

# Read data from Redis
token = "example_token"
retrieved_data = redis_manager.read_token(token)

if retrieved_data:
    print(f"Data retrieved for token '{token}': {retrieved_data}")
else:
    print(f"No data found for token '{token}'.")
