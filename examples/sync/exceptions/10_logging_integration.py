"""Demostración de integración de excepciones con logging.

Muestra cómo registrar excepciones de WRedis usando el módulo
logging estándar de Python para auditoría y diagnóstico.
"""

import logging
import sys

from wredis._exceptions import (
    CacheError,
    OperationError,
    RedisConnectionError,
    WRedisError,
)

# Configurar el logger
logger = logging.getLogger("wredis.ejemplos")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def operacion_que_falla(tipo_error):
    """Simula una operación que lanza un error específico.

    Args:
        tipo_error: Clase de excepción a lanzar.

    Raises:
        La excepción especificada.
    """
    raise tipo_error(f"Error simulado de {tipo_error.__name__}")


# Registrar errores con distintos niveles de severidad
errores_severos = [RedisConnectionError, OperationError]
errores_leves = [CacheError]

print("=== Logging de errores severos ===\n")

for tipo in errores_severos:
    try:
        operacion_que_falla(tipo)
    except WRedisError as exc:
        logger.error(
            "Error severo en operación de Redis",
            extra={
                "tipo": type(exc).__name__,
                "mensaje": str(exc),
            },
        )
        logger.debug(f"Traceback: {exc.__traceback__}")

print("\n=== Logging de errores leves ===\n")

for tipo in errores_leves:
    try:
        operacion_que_falla(tipo)
    except WRedisError as exc:
        logger.warning(
            "Error leve, se puede continuar",
            extra={
                "tipo": type(exc).__name__,
                "mensaje": str(exc),
            },
        )

# Logger personalizado que formatea excepciones de WRedis
print("\n=== Logger personalizado para WRedisError ===\n")


class WRedisLogger:
    """Logger especializado para excepciones de WRedis."""

    def __init__(self, nombre="wredis"):
        self.logger = logging.getLogger(nombre)
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            h = logging.StreamHandler(sys.stdout)
            h.setFormatter(logging.Formatter("[WREDIS] %(levelname)s: %(message)s"))
            self.logger.addHandler(h)

    def registrar_error(self, exc, contexto=None):
        """Registra una excepción de WRedis con contexto.

        Args:
            exc: La excepción capturada.
            contexto: Información adicional opcional.
        """
        if not isinstance(exc, WRedisError):
            raise TypeError(f"Se esperaba WRedisError, no {type(exc).__name__}")

        mensaje = f"{type(exc).__name__}: {exc}"
        if contexto:
            contexto_str = ", ".join(f"{k}={v}" for k, v in contexto.items())
            mensaje += f" | Contexto: {contexto_str}"

        self.logger.error(mensaje)


wlogger = WRedisLogger()

try:
    raise OperationError("SET fallido")
except WRedisError as exc:
    wlogger.registrar_error(exc, contexto={"clave": "user:1", "operacion": "SET"})

try:
    raise RedisConnectionError("Timeout tras 30s")
except WRedisError as exc:
    wlogger.registrar_error(exc, contexto={"host": "localhost", "port": 6379})
