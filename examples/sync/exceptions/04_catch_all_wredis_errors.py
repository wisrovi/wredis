"""Demostración de captura genérica con WRedisError como paraguas.

Muestra cómo capturar cualquier excepción de WRedis con un solo
bloque except, útil cuando el manejo es indiferente al tipo.
"""

from wredis._exceptions import (
    CacheError,
    ClusterError,
    OperationError,
    PubSubError,
    QueueError,
    RedisConnectionError,
    SentinelError,
    SerializationError,
    StreamError,
    TransactionError,
    ValidationError,
    WRedisError,
)


def ejecutar_operacion_riesgosa(operacion_id):
    """Simula operaciones que pueden lanzar distintos errores.

    Args:
        operacion_id: Identificador que determina qué error lanzar.

    Raises:
        Distintas excepciones según el operacion_id.
    """
    errores = {
        1: RedisConnectionError("Redis no responde"),
        2: SerializationError("No se puede serializar el objeto"),
        3: CacheError("Fallo al escribir en caché"),
        4: ValidationError("El campo 'edad' debe ser positivo"),
        5: OperationError("Operación SET fallida"),
        6: TransactionError("Conflicto en transacción WATCH"),
        7: QueueError("Cola llena"),
        8: StreamError("Stream corrupto"),
        9: PubSubError("Canal no encontrado"),
        10: SentinelError("Sentinel no disponible"),
        11: ClusterError("Nodo del cluster caído"),
    }
    raise errores.get(operacion_id, WRedisError("Error desconocido"))


# Capturar todas las excepciones de WRedis con un solo bloque
print("=== Captura genérica con WRedisError ===\n")

for op_id in range(1, 12):
    try:
        ejecutar_operacion_riesgosa(op_id)
    except WRedisError as exc:
        # Un solo bloque captura TODAS las excepciones de wredis
        print(f"Operación {op_id:2d} | {type(exc).__name__:25s} | {exc}")

# Diferenciar entre errores de WRedis y otros errores
print("\n=== Diferenciar WRedisError de otras excepciones ===\n")


def operacion_mixta(falla_con_wredis=True):
    """Simula una operación que puede fallar de formas distintas."""
    if falla_con_wredis:
        raise CacheError("Caché no disponible")
    raise ValueError("Error ajeno a WRedis")


for falla_wredis in [True, False]:
    try:
        operacion_mixta(falla_wredis)
    except WRedisError as exc:
        print(f"Error de WRedis: {type(exc).__name__} - {exc}")
    except Exception as exc:
        print(f"Error externo: {type(exc).__name__} - {exc}")
