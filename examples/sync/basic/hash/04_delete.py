"""Hash - 04_delete.py - Eliminar campos de un hash"""

from wredis.hash import RedisHashManager


def main():
    manager = RedisHashManager(host="localhost", verbose=False)

    # Crear datos
    manager.create_hash("user:2", "data", {"name": "Bob", "age": 25})

    # Eliminar un campo
    manager.delete_hash_field("user:2", "age")

    # Leer resultado
    result = manager.read_all_hash("user:2")
    print(f"Hash después de eliminar: {result}")


if __name__ == "__main__":
    main()
