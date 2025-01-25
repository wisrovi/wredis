# WRedis

**WRedis** es una librería diseñada para facilitar la interacción con Redis de forma simple y eficiente. Ofrece una API intuitiva y funcionalidades útiles para manejar conexiones, operaciones básicas y avanzadas con Redis.

# Descripción

WRedis simplifica la interacción con Redis al proporcionar:

* Métodos fáciles de usar para operaciones comunes (SET, GET, DELETE).
* Conexión rápida y eficiente con Redis.
*    Soporte para loguru y gestión de logs.
*   Extensible para proyectos más grandes.

## Instalación

Para instalar la librería, utiliza `pip`:

```bash
pip install wredis
```

Asegúrate de tener instalado Redis en tu sistema o que puedas acceder a un servidor Redis remoto. Puedes instalar Redis localmente siguiendo las [instrucciones oficiales](https://redis.io/download) o usar un ```docker-compose.yaml``` como el siguiente:

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

# Descripción

La librería **WRedis** ofrece una serie de módulos que facilitan la interacción con Redis. A continuación, se describen los módulos disponibles:

## bitmaps

### Descripción

Este módulo permite interactuar con bitmaps en Redis.

## hash

### Descripción

Este módulo permite interactuar con hashes en Redis.

## pubsub

### Descripción

Este módulo permite interactuar con el sistema de publicación y suscripción de Redis.

## queue

### Descripción

Este módulo permite interactuar con colas en Redis.

## sets

### Descripción

Este módulo permite interactuar con sets en Redis.

# sortsets

### Descripción

Este módulo permite interactuar con sorted sets en Redis.

## streams

### Descripción

Este módulo permite interactuar con streams en Redis.


# Licencia

MIT

Este proyecto está licenciado bajo la licencia MIT. Consulta el archivo ```LICENSE``` para más detalles.
