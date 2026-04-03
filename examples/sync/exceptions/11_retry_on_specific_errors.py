"""Demostración de reintentos automáticos ante errores específicos.

Implementa un decorador de reintentos que solo reintenta ante
ciertos tipos de excepciones de WRedis.
"""

import time
import random

from wredis._exceptions import (
    OperationError,
    RedisConnectionError,
    ValidationError,
    WRedisError,
)


def reintentar(max_intentos=3, espera=0.1, excepciones_reintentables=None):
    """Decorador para reintentar funciones ante errores específicos.

    Args:
        max_intentos: Número máximo de intentos.
        espera: Segundos entre reintentos.
        excepciones_reintentables: Tupla de excepciones que disparan
            reintentos. Por defecto: (RedisConnectionError, OperationError).

    Returns:
        Decorador.
    """
    if excepciones_reintentables is None:
        excepciones_reintentables = (RedisConnectionError, OperationError)

    def decorador(func):
        def wrapper(*args, **kwargs):
            ultimo_error = None
            for intento in range(1, max_intentos + 1):
                try:
                    return func(*args, **kwargs)
                except excepciones_reintentables as exc:
                    ultimo_error = exc
                    print(f"  [{func.__name__}] Intento {intento}/{max_intentos} fallido: {type(exc).__name__}: {exc}")
                    if intento < max_intentos:
                        time.sleep(espera)
                except WRedisError as exc:
                    # Errores no reintentables se propagan inmediatamente
                    print(f"  [{func.__name__}] Error no reintentable: {type(exc).__name__}: {exc}")
                    raise
            raise ultimo_error

        return wrapper

    return decorador


# Simular un cliente Redis inestable
class RedisInestable:
    """Cliente Redis que falla aleatoriamente."""

    def __init__(self):
        self._datos = {}
        self._tasa_fallo = 0.7  # 70% de probabilidad de fallo

    def get(self, clave):
        if random.random() < self._tasa_fallo:
            raise RedisConnectionError(f"Conexión perdida al hacer GET '{clave}'")
        return self._datos.get(clave)

    def set(self, clave, valor):
        if random.random() < self._tasa_fallo:
            raise OperationError(f"SET '{clave}' falló")
        self._datos[clave] = valor
        return True


# Aplicar reintentos a operaciones
cliente = RedisInestable()
random.seed(42)  # Para reproducibilidad


@reintentar(max_intentos=5, espera=0.05)
def obtener_cliente(clave):
    return cliente.get(clave)


@reintentar(max_intentos=5, espera=0.05)
def guardar_cliente(clave, valor):
    return cliente.set(clave, valor)


print("=== Reintentos con RedisConnectionError ===\n")
try:
    resultado = obtener_cliente("usuario:1")
    print(f"Éxito: {resultado}")
except RedisConnectionError as exc:
    print(f"Error tras agotar reintentos: {exc}")

print("\n=== Reintentos con OperationError ===\n")
random.seed(100)
try:
    guardar_cliente("usuario:2", {"nombre": "Bob"})
    print("Guardado exitoso")
except OperationError as exc:
    print(f"Error tras agotar reintentos: {exc}")

# Demostrar que ValidationError NO se reintenta
print("\n=== ValidationError NO se reintenta ===\n")


@reintentar(max_intentos=3, espera=0.05)
def validar_y_guardar(clave, valor):
    if not clave:
        raise ValidationError("La clave no puede estar vacía")
    return cliente.set(clave, valor)


try:
    validar_y_guardar("", "datos")
except ValidationError as exc:
    print(f"ValidationError se propagó inmediatamente: {exc}")

# Reintentos con backoff exponencial
print("\n=== Backoff exponencial ===\n")


def reintentar_con_backoff(max_intentos=4, excepciones_reintentables=None):
    """Decorador con espera exponencial entre reintentos."""
    if excepciones_reintentables is None:
        excepciones_reintentables = (RedisConnectionError, OperationError)

    def decorador(func):
        def wrapper(*args, **kwargs):
            for intento in range(1, max_intentos + 1):
                try:
                    return func(*args, **kwargs)
                except excepciones_reintentables as exc:
                    espera = 0.05 * (2 ** (intento - 1))
                    print(f"  Intento {intento}/{max_intentos} fallido, esperando {espera:.2f}s: {exc}")
                    if intento < max_intentos:
                        time.sleep(espera)
            raise exc

        return wrapper

    return decorador


random.seed(200)


@reintentar_con_backoff(max_intentos=4)
def operacion_con_backoff(clave):
    if random.random() < 0.6:
        raise RedisConnectionError(f"Fallo en GET '{clave}'")
    return "ok"


try:
    resultado = operacion_con_backoff("sesion:xyz")
    print(f"Éxito tras backoff: {resultado}")
except RedisConnectionError as exc:
    print(f"Error final: {exc}")
