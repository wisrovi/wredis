import time

from wredis.sync import RedisHashManager

redis_manager = RedisHashManager(host="localhost")

all_key = "my_hash"
redis_manager.create_hash(all_key, "user:1", {"name": "Alice", "age": 30}, ttl=60)

while True:
    if not redis_manager.exist(all_key):
        break

    user1 = redis_manager.read_hash(all_key, "user:1")
    print(f"hash exist: User 1: {user1}")

    time.sleep(10)

print("Hash not exist")
