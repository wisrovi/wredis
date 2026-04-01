"""Hash - 03_update.py - Actualizar campos en un hash"""

from wredis.hash import RedisHashManager


def main():
    manager = RedisHashManager(host="localhost", verbose=False)

    # Crear datos iniciales
    manager.create_hash("user:1", "profile", {"name": "Alice", "age": 30})

    # Actualizar el hash
    manager.update_hash("user:1", "profile", {"city": "Madrid", "country": "Spain"})

    # Leer el resultado
    result = manager.read_hash("user:1", "profile")
    print(f"Hash actualizado: {result}")


if __name__ == "__main__":
    main()
