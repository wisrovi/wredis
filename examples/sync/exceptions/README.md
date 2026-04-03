# Ejemplos de Excepciones de WRedis

Ejemplos prácticos que demuestran el uso del sistema de excepciones de `wredis._exceptions`.

## Tabla de Contenidos

| # | Archivo | Descripción |
|---|---------|-------------|
| 01 | [01_base_exception.py](01_base_exception.py) | Uso de `WRedisError` como excepción base y creación de subclases personalizadas. |
| 02 | [02_exception_hierarchy.py](02_exception_hierarchy.py) | Recorrido programático del árbol de herencia de todas las excepciones de WRedis. |
| 03 | [03_catching_specific_errors.py](03_catching_specific_errors.py) | Captura individual de cada tipo de excepción con bloques `try/except` específicos. |
| 04 | [04_catch_all_wredis_errors.py](04_catch_all_wredis_errors.py) | Captura genérica de todas las excepciones de WRedis con un solo bloque `except WRedisError`. |
| 05 | [05_custom_error_messages.py](05_custom_error_messages.py) | Creación de excepciones con mensajes detallados y atributos adicionales para diagnóstico. |
| 06 | [06_validation_error_handling.py](06_validation_error_handling.py) | Validación de claves y valores antes de enviarlos a Redis usando `ValidationError`. |
| 07 | [07_operation_error_recovery.py](07_operation_error_recovery.py) | Estrategias de recuperación ante `OperationError`: reintentos y valores fallback. |
| 08 | [08_transaction_error_handling.py](08_transaction_error_handling.py) | Manejo de `TransactionError` con reintentos optimistas y rollback simulado. |
| 09 | [09_serialization_error_handling.py](09_serialization_error_handling.py) | Detección y manejo de errores de serialización/deserialización con `SerializationError`. |
| 10 | [10_logging_integration.py](10_logging_integration.py) | Integración de excepciones de WRedis con el módulo `logging` estándar de Python. |
| 11 | [11_retry_on_specific_errors.py](11_retry_on_specific_errors.py) | Decorador de reintentos automático que solo reintenta ante errores específicos (con backoff exponencial). |
| 12 | [12_graceful_degradation.py](12_graceful_degradation.py) | Degradación elegante: continuar operando con caché en memoria cuando Redis no está disponible. |
| 13 | [13_queue_error_handling.py](13_queue_error_handling.py) | Manejo de `QueueError` en operaciones de cola: push, pop, peek y procesamiento seguro. |
| 14 | [14_stream_and_pubsub_errors.py](14_stream_and_pubsub_errors.py) | Manejo combinado de `StreamError` y `PubSubError` en operaciones de streams y pub/sub. |
| 15 | [15_custom_error_handler.py](15_custom_error_handler.py) | Creación de un manejador centralizado de errores con registro de callbacks y decorador personalizado. |

## Jerarquía de Excepciones

```
WRedisError (base)
├── RedisConnectionError     — Fallos de conexión
├── SerializationError       — Errores de serialización/deserialización
├── CacheError               — Fallos en operaciones de caché
├── SentinelError            — Errores en operaciones Sentinel
├── ClusterError             — Errores en operaciones Cluster
├── ValidationError          — Fallos de validación de entrada
├── OperationError           — Fallos en operaciones Redis generales
├── TransactionError         — Fallos en transacciones (WATCH conflicts)
├── QueueError               — Fallos en operaciones de cola
├── StreamError              — Fallos en operaciones de stream
└── PubSubError              — Fallos en operaciones pub/sub
```

## Ejecutar los ejemplos

```bash
# Ejecutar un ejemplo individual
python examples/sync/exceptions/01_base_exception.py

# Ejecutar todos los ejemplos
for f in examples/sync/exceptions/*.py; do echo "=== $f ==="; python "$f"; echo; done
```
