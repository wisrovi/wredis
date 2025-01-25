# Examples

This directory contains a collection of examples that demonstrate the usage of various modules and functionalities in this project. Each subfolder corresponds to a specific module and includes example scripts to help you understand how to use that module.

## Directory Structure

The examples are organized as follows:

```
examples/
    sorted_set.py/
        read.py
        write.py
    sets/
        read.py
        write.py
    pub_sub/
        consumer.py
        producer.py
    queue/
        consumer.py
        producer.py
    streams/
        consume.py
        producer.py
    bitmap/
        read.py
        write.py
    hash/
        read.py
        write.py
```

## How to Use

1. Navigate to the module folder of interest, e.g., `examples/module1/`.
2. Open the `README.md` in that folder to get detailed information about the examples.
3. Run the scripts directly using:
   ```bash
   python example1.py
   ```

## Modules and Examples

### bitmap

#### Description
This module demonstrates specific functionalities.


- **read.py**: Example demonstrating functionality.

```python
from wredis.bitmap import RedisBitmapManager
bitmap_manager = RedisBitmapManager(host="localhost")
print(bitmap_manager.get_bit("my_bitmap", 0))
print(bitmap_manager.count_bits("my_bitmap"))
```



- **write.py**: Example demonstrating functionality.
```python
from a_wredis import RedisBitmapManager


bitmap_manager = RedisBitmapManager(host="localhost")

bitmap_manager.set_bit(key="my_bitmap", offset=5, value=1)
  ```



### hash

#### Description
This module demonstrates specific functionalities.


- **read.py**: Example demonstrating functionality.
```python
from wredis.hash import RedisHashManager


if __name__ == "__main__":
    # Crear una instancia de RedisHashManager
    redis_manager = RedisHashManager(host="localhost")

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
  ```


- **write.py**: Example demonstrating functionality.
```python
from wredis.hash import RedisHashManager


if __name__ == "__main__":
    # Crear una instancia de RedisHashManager
    redis_manager = RedisHashManager(host="localhost")

    # Escribir valores en un hash
    redis_manager.create_hash("my_hash", "user:1", {"name": "Alice", "age": 30}, ttl=60)
    redis_manager.create_hash("my_hash", "user:2", {"name": "Bob", "age": 25})
    redis_manager.create_hash("my_hash", "user:3", {"name": "Bob", "age": 25})
    redis_manager.create_hash("my_hash", "user:4", {"name": "Bob", "age": 25})
  ```



### pub_sub

#### Description
This module demonstrates specific functionalities.


- **consumer.py**: Example demonstrating functionality.
```python
from wredis.pubsub import RedisPubSubManager
import signal

pubsub_manager = RedisPubSubManager(host="localhost", verbose=False)


@pubsub_manager.on_message("channel_1")
def handle_message(message):
    print(f"[channel_1] Mensaje recibido: {message}")


@pubsub_manager.on_message("channel_2")
def handle_channel_2(message):
    print(f"[channel_2] Mensaje recibido: {message}")


# Manejar la señal de interrupción (Ctrl+C) para salir limpiamente
def signal_handler(sig, frame):
    print("\nDeteniendo programa...")
    pubsub_manager.stop_listeners()
    print("Programa detenido.")
    exit(0)


signal.signal(signal.SIGINT, signal_handler)

signal.pause()
  ```


- **producer.py**: Example demonstrating functionality.
```python
from wredis.pubsub import RedisPubSubManager


pubsub_manager = RedisPubSubManager(host="localhost")


pubsub_manager.publish_message("channel_1", "Hello, Redis!")


pubsub_manager.publish_message("channel_2", {"saludo": "Hola desde channel_2!"})
  ```



### queue

#### Description
This module demonstrates specific functionalities.


- **consumer.py**: Example demonstrating functionality.
```python
from wredis.queue import RedisQueueManager


# Crear una instancia del consumidor
queue_manager = RedisQueueManager(poll_interval=2, host="localhost", verbose=False)


@queue_manager.on_message("4090")
def worker(record):

    global conteo_global_queso

    """
    Procesa un registro de la cola 'queue_1'.
    """
    print(f"Procesando de 'queue_1': {record}")


@queue_manager.on_message("queue:4060")
def worker(record):

    global conteo_global_queso

    """
    Procesa un registro de la cola 'queue_1'.
    """
    print(f"Procesando de 'queue_1': {record}")


@queue_manager.on_message("4060")
def worker(record):

    global conteo_global_queso

    """
    Procesa un registro de la cola 'queue_1'.
    """
    print(f"Procesando de 'queue_1': {record}")


# Verificar la longitud de la cola
queue_length = queue_manager.get_queue_length("tasks")


queue_manager.start()

# Mantener el programa activo
queue_manager.wait()
  ```


- **producer.py**: Example demonstrating functionality.
```python
from wredis.queue import RedisQueueManager


# Crear una instancia del productor
queue_manager = RedisQueueManager(host="localhost")

# Publicar mensajes en diferentes colas
queue_manager.publish("4090", {"id": 1, "task": "process_image", "status": "pending"})
queue_manager.publish("4060", {"id": 2, "task": "generate_report", "priority": "high"})
queue_manager.publish(
    "queue:4060", {"id": 3, "task": "process_video", "status": "pending"}
)

queue_manager.publish("tasks", {"task_id": 3, "description": "Generar reporte"}, ttl=30)
queue_manager.publish(
    "tasks", {"task_id": 4, "description": "Actualizar base de datos"}, ttl=120
)
queue_manager.publish(
    "tasks",
    {
        "task_id": 4,
        "description": {"id": 2, "task": "generate_report", "priority": "high"},
    },
    ttl=10,
)


# NOTA: ajusta un TTL modifica el tiempo de toda la cola y no de un mensaje en particular
# NOTA: el TTL se mide en segundos
  ```



### sets

#### Description
This module demonstrates specific functionalities.


- **read.py**: Example demonstrating functionality.
```python
from wredis.sets import RedisSetManager


set_manager = RedisSetManager(host="localhost")


print(set_manager.get_set_members("my_set"))
  ```


- **write.py**: Example demonstrating functionality.
```python
from wredis.sets import RedisSetManager

set_manager = RedisSetManager(host="localhost")

set_manager.add_to_set("my_set", "value1", "value2")
set_manager.add_to_set("my_set", "value5", "value2")
set_manager.add_to_set("my_set", "value1", "value8")
  ```



### sorted_set.py

#### Description
This module demonstrates specific functionalities.


- **read.py**: Example demonstrating functionality.
```python
from wredis.sortedset import RedisSortedSetManager


sorted_set_manager = RedisSortedSetManager(host="localhost")


items = sorted_set_manager.get_sorted_set("my_sorted_set", with_scores=True)
items_reverse = sorted_set_manager.get_sorted_set_reverse("my_sorted_set")
# Obtener rank y score
rank = sorted_set_manager.get_rank("my_sorted_set", "item1")
score = sorted_set_manager.get_score("my_sorted_set", "item2")

# Eliminar un miembro
sorted_set_manager.remove_from_sorted_set("my_sorted_set", "item1")

# Eliminar todo el conjunto ordenado
# sorted_set_manager.delete_sorted_set("my_sorted_set")


print(items)
print(items_reverse)
print(rank)
print(score)
  ```


- **write.py**: Example demonstrating functionality.
```python
from wredis.sortedset import RedisSortedSetManager


sorted_set_manager = RedisSortedSetManager(host="localhost", verbose=False)

sorted_set_manager.add_to_sorted_set("my_sorted_set", 1, "item1")
sorted_set_manager.add_to_sorted_set("my_sorted_set", 3, "item3")
sorted_set_manager.add_to_sorted_set("my_sorted_set", 2, "item2")

sorted_set_manager.add_to_sorted_set("my_sorted_set", 1, "item1")
sorted_set_manager.add_to_sorted_set(key="my_sorted_set", score=5, member="item5")
  ```



### streams

#### Description
This module demonstrates specific functionalities.


- **consume.py**: Example demonstrating functionality.
```python
from wredis.streams import RedisStreamManager


stream_manager = RedisStreamManager(host="localhost", verbose=False)


# Registrar un consumidor para un stream
@stream_manager.on_message(
    stream_name="my_stream", group_name="my_group", consumer_name="consumer_1"
)
def process_message(data):
    print(f"[Consumer 1] Procesando mensaje: {data}")


# Registrar el segundo consumidor
@stream_manager.on_message(
    stream_name="my_stream_2", group_name="my_group", consumer_name="consumer_2"
)
def process_message_consumer_2(data):
    print(f"[Consumer 2] Procesando mensaje: {data}")


# Mantener el programa activo para consumir mensajes
stream_manager.wait()
  ```


- **producer.py**: Example demonstrating functionality.
```python
from wredis.streams import RedisStreamManager


stream_manager = RedisStreamManager(host="localhost")

stream_manager.add_to_stream("my_stream", {"field1": "value1"})
stream_manager.add_to_stream("my_stream", {"field2": "value3", "field4": "value4"})


stream_manager.add_to_stream("my_stream_2", {"field1": "value1"})
  ```


