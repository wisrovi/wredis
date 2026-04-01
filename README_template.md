# WRedis

**WRedis** es una librería diseñada para facilitar la interacción con Redis de forma simple y eficiente. Ofrece una API intuitiva y funcionalidades útiles para manejar conexiones, operaciones básicas y avanzadas con Redis.

## Descripción

WRedis simplifica la interacción con Redis al proporcionar:

- Métodos fáciles de usar para operaciones comunes (SET, GET, DELETE, gestión de TTL).
- Conexión rápida y eficiente con Redis.
- Soporte para loguru y gestión de logs.
- Registro de consumidores basado en decoradores para Pub/Sub, Colas y Streams.
- Consumo paralelo con hilos para colas y streams.
- Extensible para proyectos más grandes.

## Instalación

Para instalar la librería, utiliza `pip`:

```bash
pip install wredis
```

Asegúrate de tener instalado Redis en tu sistema o que puedas acceder a un servidor Redis remoto. Puedes instalar Redis localmente siguiendo las [instrucciones oficiales](https://redis.io/download) o usar un `docker-compose.yaml` como el siguiente:

```yaml
version: "3.3"
services:
  redis:
    image: redislabs/redismod
    ports:
      - "6379:6379"
    environment:
      - SO=docker
    volumes:
      - ./cache_redis:/data
    command: --dir /data --loadmodule /usr/lib/redis/modules/redistimeseries.so

  redis-commander:
    image: rediscommander/redis-commander:latest
    environment:
      - REDIS_HOSTS=local:redis:6379
      - HTTP_USER=root
      - HTTP_PASSWORD=qwerty
    ports:
      - "8081:8081"
    depends_on:
      - redis
```

## Módulos

La librería **WRedis** ofrece una serie de módulos que facilitan la interacción con Redis:

---

## Bitmaps

**Clase:** `RedisBitmapManager`

Este módulo permite interactuar con bitmaps en Redis.

### Constructor

```python
RedisBitmapManager(host="localhost", port=6379, db=0, verbose=True)
```

### Métodos

| Método | Descripción |
|--------|-------------|
| `set_bit(key, offset, value, ttl=-1)` | Establece un bit en una posición específica. Opcionalmente configura TTL. |
| `get_bit(key, offset)` | Obtiene el valor de un bit en una posición específica (0 o 1). |
| `count_bits(key)` | Cuenta el número de bits establecidos en 1. |
| `get_ttl(key)` | Obtiene el TTL de una clave bitmap. Retorna -1 (sin TTL), -2 (no existe), o segundos restantes. |
| `extend_ttl(key, ttl)` | Extiende o establece un nuevo TTL para una clave bitmap. |

---

## Hash

**Clase:** `RedisHashManager`

Este módulo permite interactuar con hashes en Redis. Soporta serialización automática JSON para valores tipo dict.

### Constructor

```python
RedisHashManager(host="localhost", port=6379, db=0, verbose=True)
```

### Métodos

| Método | Descripción |
|--------|-------------|
| `create_hash(hash_name, key, value, ttl=-1)` | Escribe un par clave-valor en un hash. Los dict se serializan a JSON automáticamente. |
| `read_hash(hash_name, key)` | Lee un valor del hash. Deserializa JSON si aplica. Retorna `None` si no existe. |
| `update_hash(hash_name, key, new_data)` | Actualiza un par clave-valor. Si existe y es dict, fusiona los datos. |
| `delete_hash_field(hash_name, key)` | Elimina un campo específico del hash. |
| `read_all_hash(hash_name)` | Lee todos los campos y valores del hash. Retorna un dict o `None`. |
| `get_ttl(hash_name)` | Obtiene el TTL de un hash. |
| `extend_ttl(hash_name, ttl)` | Extiende o establece un nuevo TTL para un hash. |

---

## Pub/Sub

**Clase:** `RedisPubSubManager`

Este módulo permite interactuar con el sistema de publicación y suscripción de Redis usando una API basada en decoradores.

### Constructor

```python
RedisPubSubManager(host="localhost", port=6379, db=0, verbose=True)
```

### Métodos

| Método | Descripción |
|--------|-------------|
| `publish_message(channel, message)` | Publica un mensaje en un canal. Soporta strings y dicts (auto-serializados a JSON). |
| `on_message(channel)` | Decorador para registrar una función callback para un canal específico. |
| `stop_listeners()` | Detiene todos los hilos de escucha. |

---

## Queue

**Clase:** `RedisQueueManager`

Este módulo permite interactuar con colas en Redis usando listas (`RPUSH`/`BRPOP`).

### Constructor

```python
RedisQueueManager(poll_interval=1, host="localhost", port=6379, db=0, max_retries=3, verbose=True)
```

### Métodos

| Método | Descripción |
|--------|-------------|
| `publish(queue_name, data, ttl=-1)` | Publica un mensaje (dict) en una cola. Auto-serializado a JSON. |
| `on_message(queue_name)` | Decorador para registrar una función callback para una cola específica. |
| `start()` | Inicia hilos de consumo paralelo para todas las colas registradas. |
| `stop()` | Detiene el consumo de todas las colas. |
| `wait()` | Mantiene el programa activo y maneja SIGINT para cierre limpio. |
| `get_queue_length(queue_name)` | Retorna el número de elementos en una cola. |

---

## Sets

**Clase:** `RedisSetManager`

Este módulo permite interactuar con sets en Redis.

### Constructor

```python
RedisSetManager(host="localhost", port=6379, db=0, verbose=True)
```

### Métodos

| Método | Descripción |
|--------|-------------|
| `add_to_set(key, *values, ttl=-1)` | Agrega uno o más elementos a un set. Opcionalmente configura TTL. |
| `get_set_members(key)` | Obtiene todos los miembros de un set como un `set` decodificado. |
| `is_member(key, value)` | Verifica si un elemento es miembro del set. Retorna `True` o `False`. |
| `remove_from_set(key, *values)` | Elimina uno o más elementos de un set. |
| `get_ttl(key)` | Obtiene el TTL de un set. |
| `extend_ttl(key, ttl)` | Extiende o establece un nuevo TTL para un set. |

---

## Sorted Sets

**Clase:** `RedisSortedSetManager`

Este módulo permite interactuar con sorted sets en Redis.

### Constructor

```python
RedisSortedSetManager(host="localhost", port=6379, db=0, verbose=True)
```

### Métodos

| Método | Descripción |
|--------|-------------|
| `add_to_sorted_set(key, score, member, ttl=-1)` | Agrega un miembro con un score. Opcionalmente configura TTL. |
| `get_sorted_set(key, start=0, stop=-1, with_scores=False)` | Obtiene elementos en orden ascendente. |
| `get_sorted_set_reverse(key, start=0, stop=-1, with_scores=False)` | Obtiene elementos en orden descendente. |
| `remove_from_sorted_set(key, member)` | Elimina un miembro del sorted set. |
| `get_rank(key, member)` | Obtiene el rank (índice base 0) de un miembro. |
| `get_score(key, member)` | Obtiene el score de un miembro. |
| `delete_sorted_set(key)` | Elimina todo el sorted set. |
| `set_ttl(key, ttl)` | Establece un TTL para un sorted set existente. |
| `get_ttl(key)` | Obtiene el TTL de un sorted set. |
| `increment_score(key, increment, member)` | Incrementa el score de un miembro. |
| `get_sorted_set_by_score(key, min_score, max_score, with_scores=False)` | Obtiene miembros dentro de un rango de scores. |

---

## Streams

**Clase:** `RedisStreamManager`

Este módulo permite interactuar con Redis Streams usando consumer groups.

### Constructor

```python
RedisStreamManager(host="localhost", port=6379, db=0, verbose=True)
```

### Métodos

| Método | Descripción |
|--------|-------------|
| `add_to_stream(key, data, ttl=None)` | Agrega un mensaje a un stream. Retorna el ID del mensaje. |
| `on_message(stream_name, group_name, consumer_name)` | Decorador para registrar un consumidor. Crea el consumer group si no existe. |
| `read_from_stream(key, count=1, block=None)` | Lee mensajes de un stream sin un consumidor registrado. |
| `wait()` | Mantiene el programa activo y maneja SIGINT para cierre limpio. |

---

## Licencia

MIT

Este proyecto está licenciado bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
