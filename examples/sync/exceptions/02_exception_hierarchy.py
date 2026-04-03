"""Demostración de la jerarquía completa de excepciones de WRedis.

Recorre programáticamente el árbol de excepciones para visualizar
cómo todas las excepciones especializadas heredan de WRedisError.
"""

import inspect

from wredis import _exceptions


def mostrar_jerarquia():
    """Imprime el árbol de herencia de las excepciones de WRedis."""
    base = _exceptions.WRedisError
    print("Jerarquía de excepciones de WRedis:")
    print(f"  {base.__name__} (base)")

    # Obtener todas las clases del módulo que hereden de WRedisError
    for nombre, clase in inspect.getmembers(_exceptions, inspect.isclass):
        if issubclass(clase, base) and clase is not base:
            print(f"    └── {nombre}")
            # Mostrar atributos propios si los tiene
            if clase.__doc__:
                print(f"        Doc: {clase.__doc__}")


mostrar_jerarquia()

# Verificar relaciones de herencia
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

excepciones = [
    RedisConnectionError,
    SerializationError,
    CacheError,
    SentinelError,
    ClusterError,
    ValidationError,
    OperationError,
    TransactionError,
    QueueError,
    StreamError,
    PubSubError,
]

print("\nVerificación de herencia:")
for exc_cls in excepciones:
    es_subclase = issubclass(exc_cls, WRedisError)
    print(f"  {exc_cls.__name__} -> WRedisError: {es_subclase}")
