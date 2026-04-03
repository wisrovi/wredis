"""Demostración de captura de errores específicos con try/except.

Muestra cómo capturar excepciones individuales de WRedis
para manejar cada tipo de error de forma diferenciada.
"""

from wredis._exceptions import (
    CacheError,
    OperationError,
    RedisConnectionError,
    ValidationError,
)


def simular_operacion(tipo_error):
    """Simula una operación que puede fallar de distintas maneras.

    Args:
        tipo_error: El tipo de excepción a lanzar.

    Raises:
        La excepción especificada.
    """
    raise tipo_error(f"Error simulado: {tipo_error.__name__}")


# Capturar cada tipo de error por separado
tipos_a_probar = [
    RedisConnectionError,
    ValidationError,
    CacheError,
    OperationError,
]

for tipo in tipos_a_probar:
    try:
        simular_operacion(tipo)
    except RedisConnectionError as exc:
        print(f"[CONEXIÓN] No se pudo conectar: {exc}")
    except ValidationError as exc:
        print(f"[VALIDACIÓN] Datos inválidos: {exc}")
    except CacheError as exc:
        print(f"[CACHE] Fallo en caché: {exc}")
    except OperationError as exc:
        print(f"[OPERACIÓN] Error en operación: {exc}")

# Demostrar que el orden de los except importa
print("\n--- Orden correcto de captura ---")
try:
    raise RedisConnectionError("Servidor no disponible")
except RedisConnectionError as exc:
    # Este bloque se ejecuta primero porque es más específico
    print(f"Capturado como RedisConnectionError: {exc}")

# Si se captura WRedisError primero, los bloques específicos nunca se ejecutan
print("\n--- Orden incorrecto (WRedisError primero) ---")
from wredis._exceptions import WRedisError

try:
    raise RedisConnectionError("Servidor no disponible")
except WRedisError as exc:
    # Captura TODO, los bloques específicos debajo no se ejecutarían
    print(f"Capturado como WRedisError (demasiado genérico): {exc}")
