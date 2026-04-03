# AsyncBaseManager - Ejemplos

Colección de ejemplos prácticos que demuestran el uso de `AsyncBaseManager` de wredis para operaciones asíncronas con Redis.

Todos los ejemplos utilizan `fakeredis.aioredis` como backend de prueba, por lo que no requieren un servidor Redis real para ejecutarse.

## Requisitos

```bash
pip install wredis fakeredis
```

## Ejecutar un ejemplo

```bash
python examples/async/async_base/01_basic_init.py
```

## Tabla de Contenidos

| # | Archivo | Descripción |
|---|---------|-------------|
| 01 | [01_basic_init.py](01_basic_init.py) | **Inicialización básica** - Cómo crear una instancia de `AsyncBaseManager` con parámetros por defecto y realizar operaciones básicas de SET/GET. |
| 02 | [02_health_check.py](02_health_check.py) | **Verificación de salud** - Uso del método `health_check()` para verificar la conectividad con Redis antes de realizar operaciones críticas. |
| 03 | [03_async_context_manager.py](03_async_context_manager.py) | **Contexto asíncrono** - Uso de `async with` para gestión automática del ciclo de vida de la conexión, asegurando cierre limpio. |
| 04 | [04_execute_with_retry.py](04_execute_with_retry.py) | **Ejecución con reintentos** - El método `_execute()` con lógica de reintento exponencial (3 intentos, backoff 0.1s, 0.2s). |
| 05 | [05_fastapi_integration.py](05_fastapi_integration.py) | **Integración con FastAPI** - Patrón básico de integración con FastAPI usando lifespan para gestión de conexión. |
| 06 | [06_concurrent_operations.py](06_concurrent_operations.py) | **Operaciones concurrentes** - Uso de `asyncio.gather()` para ejecutar múltiples operaciones de Redis de forma concurrente. |
| 07 | [07_connection_pooling.py](07_connection_pooling.py) | **Pool de conexiones** - Configuración avanzada del pool: `max_connections`, `socket_timeout`, `decode_responses`. |
| 08 | [08_error_handling.py](08_error_handling.py) | **Manejo de errores** - Estrategias de error handling: try/except con `OperationError`, graceful degradation y fallbacks. |
| 09 | [09_custom_async_manager.py](09_custom_async_manager.py) | **Manager personalizado** - Herencia de `AsyncBaseManager` para crear un `SessionManager` con métodos específicos. |
| 10 | [10_logging_integration.py](10_logging_integration.py) | **Logging integrado** - Uso del método `log()` con diferentes niveles (info, debug, warning, error) integrado con loguru. |
| 11 | [11_multiple_databases.py](11_multiple_databases.py) | **Múltiples bases de datos** - Conexión simultánea a diferentes DBs de Redis (db=0, db=1, db=2) con aislamiento verificado. |
| 12 | [12_async_worker_pattern.py](12_async_worker_pattern.py) | **Patrón Worker/Producer** - Implementación de cola de mensajes con productor y consumidor usando LPUSH/RPOP. |
| 13 | [13_async_cache_decorator.py](13_async_cache_decorator.py) | **Decorador de caché** - Decorador personalizado `@async_cache` para cachear resultados de funciones asíncronas con TTL. |
| 14 | [14_rate_limiter.py](14_rate_limiter.py) | **Rate Limiter** - Limitador de tasa con algoritmo sliding window log usando sorted sets de Redis. |
| 15 | [15_fastapi_advanced.py](15_fastapi_advanced.py) | **FastAPI avanzado** - Integración completa con middleware de rate limiting, caché de respuestas y gestión de sesiones. |

## API de AsyncBaseManager

```python
AsyncBaseManager(
    host="localhost",
    port=6379,
    db=0,
    password=None,
    ssl=False,
    socket_timeout=5.0,
    max_connections=10,
    decode_responses=False,
    verbose=True,
)
```

### Métodos principales

| Método | Descripción |
|--------|-------------|
| `await manager.health_check()` | Verifica conexión con Redis. Retorna `bool`. |
| `manager.log(message, level)` | Registra mensaje con loguru si verbose=True. |
| `await manager._execute(operation, *args, **kwargs)` | Ejecuta operación con reintentos. Retorna resultado. |
| `await manager.close()` | Cierra el pool de conexiones. |
| `async with AsyncBaseManager() as m:` | Context manager para gestión automática. |
