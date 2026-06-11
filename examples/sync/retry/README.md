# Ejemplos de Retry en WRedis

Coleccion de 15 ejemplos practicos que demuestran el uso de los decoradores `retry` y `async_retry` de WRedis para crear codigo resiliente ante fallos temporales.

## API de Reintento

| Decorador | Descripcion |
|-----------|-------------|
| `@retry(max_attempts, delay, backoff, exceptions)` | Decorador sincrono con backoff exponencial |
| `@async_retry(max_attempts, delay, backoff, exceptions)` | Decorador async con `asyncio.sleep` |

**Import:** `from wredis._retry import retry, async_retry`

## Ejemplos

| # | Archivo | Descripcion |
|---|---------|-------------|
| 01 | [01_basic_retry.py](01_basic_retry.py) | Uso basico del decorador `@retry` con una function que falla intermitentemente |
| 02 | [02_custom_exceptions.py](02_custom_exceptions.py) | Configuracion de excepciones personalizadas para capturar errores especificos |
| 03 | [03_backoff_timing.py](03_backoff_timing.py) | Medicion y demostracion del backoff exponencial entre reintentos |
| 04 | [04_redis_read_operations.py](04_redis_read_operations.py) | Reintento en operaciones de lectura (GET) de Redis |
| 05 | [05_redis_write_operations.py](05_redis_write_operations.py) | Reintento en operaciones de escritura (SET/HSET) de Redis |
| 06 | [06_database_connection.py](06_database_connection.py) | Establecimiento resiliente de conexiones a Redis |
| 07 | [07_api_calls.py](07_api_calls.py) | Reintento en llamadas a APIs externas (clima, notificaciones) |
| 08 | [08_circuit_breaker.py](08_circuit_breaker.py) | Patron circuit breaker combinado con retry para proteger servicios |
| 09 | [09_retry_with_logging.py](09_retry_with_logging.py) | Logging y monitoreo de estadisticas de reintentos |
| 10 | [10_retry_with_wrapper.py](10_retry_with_wrapper.py) | Decorador wrapper que combina validacion con reintento |
| 11 | [11_batch_operations.py](11_batch_operations.py) | Reintento en operaciones por lotes (batch processing) |
| 12 | [12_retry_with_fallback.py](12_retry_with_fallback.py) | Patron de cache local como fallback cuando Redis falla |
| 13 | [13_retry_with_timeout.py](13_retry_with_timeout.py) | Limitacion del tiempo total de reintentos con timeout |
| 14 | [14_async_retry.py](14_async_retry.py) | Uso del decorador `@async_retry` con funciones async/await |
| 15 | [15_async_retry_fastapi.py](15_async_retry_fastapi.py) | Integracion de `@async_retry` con endpoints estilo FastAPI |

## Parametros del Decorador

- **`max_attempts`** (int): Numero maximo de intentos (default: 3)
- **`delay`** (float): Delay initial entre reintentos en segundos (default: 0.1)
- **`backoff`** (float): Multiplicador del delay tras cada reintento (default: 2.0)
- **`exceptions`** (tuple): Tupla de tipos de excepcion que disparan el reintento (default: `(redis.ConnectionError, redis.TimeoutError)`)

## Ejemplo Rapido

```python
from wredis._retry import retry
import redis

@retry(max_attempts=3, delay=0.5, backoff=2.0)
def operacion_critica():
    return redis_client.get("clave_importante")
```

## Notas

- Todos los ejemplos usan mocks para similar fallos de Redis sin necesidad de un servidor real
- Las excepciones no incluidas en `exceptions` se propagan inmediatamente sin reintento
- Tras agotar los intentos, se lanza `OperationError` de `wredis._exceptions`
