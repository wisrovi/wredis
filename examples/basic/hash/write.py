from wredis.hash import RedisHashManager


if __name__ == "__main__":
    # Crear una instancia de RedisHashManager
    redis_manager = RedisHashManager(host="localhost")

    # Escribir valores en un hash
    redis_manager.create_hash("my_hash", "user:1", {"name": "Alice", "age": 30}, ttl=60)
    redis_manager.create_hash("my_hash", "user:2", {"name": "Bob", "age": 25})
    redis_manager.create_hash("my_hash", "user:3", {"name": "Bob", "age": 25})
    redis_manager.create_hash("my_hash", "user:4", {"name": "Bob", "age": 25})
