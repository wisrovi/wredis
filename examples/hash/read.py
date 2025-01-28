from wredis.hash import RedisHashManager


if __name__ == "__main__":
    redis_manager = RedisHashManager(host="localhost", verbose=False)


    # Leer valores específicos del hash
    user1 = redis_manager.read_hash("my_hash", "user:1")
    print(f"Usuario 1: {user1}")

    # Leer todos los campos del hash
    all_users = redis_manager.read_all_hash("my_hash")
    print(f"Todos los usuarios: {all_users}")

    # Agregar un nuevo campo si no existe
    redis_manager.update_hash(
        "my_hash", "user:3", {"name": "William", "age": 35, "gender": "male"}
    )
    
    # Agregar un nuevo campo si no existe
    redis_manager.update_hash(
        "my_hash", "user:5", {"name": "William", "age": 35, "gender": "male"}
    )

    # Eliminar un campo específico
    redis_manager.delete_hash_field("my_hash", "user:2")

    # Leer el hash después de eliminar un campo
    all_users_after_deletion = redis_manager.read_all_hash("my_hash")
    print(f"Usuarios después de eliminación: {all_users_after_deletion}")
