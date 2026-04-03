# BaseManager Examples - wredis

Ejemplos prácticos de uso de `wredis._base.BaseManager`, la clase base para todos los gestores sincrónicos de Redis en wredis.

Cada ejemplo es un script de Python funcional que utiliza `fakeredis` para las pruebas, por lo que no se requiere un servidor Redis real.

## Tabla de Contenidos

| # | Archivo | Descripción |
|---|---------|-------------|
| 01 | [01_basic_init.py](01_basic_init.py) | Inicialización básica de BaseManager con parámetros por defecto y verificación de conexión. |
| 02 | [02_custom_config.py](02_custom_config.py) | Configuración personalizada: host, puerto, base de datos, timeout, máximo de conexiones y más. |
| 03 | [03_health_check.py](03_health_check.py) | Verificación del estado de la conexión usando `health_check()` y PING. |
| 04 | [04_context_manager.py](04_context_manager.py) | Uso de BaseManager como gestor de contexto con `with` para liberación automática de recursos. |
| 05 | [05_execute_with_retry.py](05_execute_with_retry.py) | Ejecución de operaciones con reintentos automáticos usando `_execute()` y backoff exponencial. |
| 06 | [06_logging.py](06_logging.py) | Sistema de logging integrado con `log()` y diferentes niveles (debug, info, warning, error). |
| 07 | [07_connection_pooling.py](07_connection_pooling.py) | Gestión del pool de conexiones interno y configuración del número máximo de conexiones. |
| 08 | [08_error_handling.py](08_error_handling.py) | Manejo de errores con excepciones personalizadas como `OperationError`. |
| 09 | [09_custom_manager.py](09_custom_manager.py) | Creación de un gestor personalizado extendiendo BaseManager (ejemplo: gestor de caché con TTL). |
| 10 | [10_multiple_instances.py](10_multiple_instances.py) | Creación y gestión de múltiples instancias independientes conectadas a diferentes bases de datos. |
| 11 | [11_batch_operations.py](11_batch_operations.py) | Operaciones por lotes: inserción masiva, listas, hashes y conjuntos con `_execute()`. |
| 12 | [12_verbose_mode.py](12_verbose_mode.py) | Diferencias entre modo verbose y silencioso, incluyendo cambio dinámico del modo. |
| 13 | [13_unit_testing.py](13_unit_testing.py) | Pruebas unitarias con fakeredis: health check, CRUD, listas, hashes, context manager y verbose. |
| 14 | [14_pipeline_operations.py](14_pipeline_operations.py) | Uso de pipelines de Redis para ejecutar múltiples operaciones de forma atómica y eficiente. |
| 15 | [15_connection_pool_monitoring.py](15_connection_pool_monitoring.py) | Monitoreo del pool de conexiones: métricas, estado, información del cliente y verificación de salud. |

## Requisitos

```bash
pip install fakeredis wredis
```

## Ejecutar ejemplos

Cada ejemplo es un script independiente que se puede ejecutar directamente:

```bash
python examples/sync/base_manager/01_basic_init.py
python examples/sync/base_manager/05_execute_with_retry.py
python examples/sync/base_manager/09_custom_manager.py
```

## API de BaseManager

La clase `BaseManager` proporciona:

- **`__init__`**: Constructor con parámetros de conexión (host, port, db, password, socket_timeout, max_connections, decode_responses, verbose)
- **`health_check()`**: Verifica que la conexión esté activa (devuelve `bool`)
- **`log(message, level)`**: Registra mensajes con loguru si verbose está activado
- **`_execute(operation, *args, **kwargs)`**: Ejecuta operaciones Redis con reintentos automáticos
- **`close()`**: Cierra el pool de conexiones
- **Context manager**: Soporte para `with BaseManager() as m: ...`

## Estructura

```
base_manager/
├── README.md                          # Este archivo
├── 01_basic_init.py                   # Inicialización básica
├── 02_custom_config.py                # Configuración personalizada
├── 03_health_check.py                 # Verificación de salud
├── 04_context_manager.py              # Gestor de contexto
├── 05_execute_with_retry.py           # Ejecución con reintentos
├── 06_logging.py                      # Sistema de logging
├── 07_connection_pooling.py           # Pool de conexiones
├── 08_error_handling.py               # Manejo de errores
├── 09_custom_manager.py               # Gestor personalizado
├── 10_multiple_instances.py           # Múltiples instancias
├── 11_batch_operations.py             # Operaciones por lotes
├── 12_verbose_mode.py                 # Modo verbose
├── 13_unit_testing.py                 # Pruebas unitarias
├── 14_pipeline_operations.py          # Pipeline de operaciones
└── 15_connection_pool_monitoring.py   # Monitoreo del pool
```
