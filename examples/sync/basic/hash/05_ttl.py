"""Hash - 05_ttl.py - Manejo de TTL en hashes"""

from wredis.hash import RedisHashManager


def main():
    manager = RedisHashManager(host="localhost", verbose=False)

    # Crear hash con TTL
    manager.create_hash("temp:data", "key1", {"value": "expirable"}, ttl=10)

    # Ver TTL
    ttl = manager.get_ttl("temp:data")
    print(f"TTL剩余: {ttl} segundos")

    # Extender TTL
    manager.extend_ttl("temp:data", 60)
    new_ttl = manager.get_ttl("temp:data")
    print(f"Nuevo TTL: {new_ttl} segundos")


if __name__ == "__main__":
    main()
