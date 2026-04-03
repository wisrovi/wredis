"""Demostración de recuperación ante OperationError.

Muestra cómo detectar OperationError y aplicar estrategias de
recuperación como reintentos o operaciones alternativas.
"""

import time

from wredis._exceptions import OperationError


class RedisSimulado:
    """Simula un cliente Redis que puede fallar temporalmente."""

    def __init__(self):
        self._datos = {}
        self._fallar = True
        self._intentos = 0

    def simular_recuperacion(self):
        """Hace que las operaciones empiecen a tener éxito."""
        self._fallar = False

    def get(self, clave):
        """Simula un GET que puede fallar."""
        self._intentos += 1
        if self._fallar:
            raise OperationError(f"GET '{clave}' falló (intento {self._intentos})")
        return self._datos.get(clave)

    def set(self, clave, valor):
        """Simula un SET que puede fallar."""
        self._intentos += 1
        if self._fallar:
            raise OperationError(f"SET '{clave}' falló (intento {self._intentos})")
        self._datos[clave] = valor
        return True


def operacion_con_reintento(cliente, operacion, max_intentos=3):
    """Ejecuta una operación con reintentos ante OperationError.

    Args:
        cliente: Instancia de RedisSimulado.
        operacion: Función que ejecuta la operación.
        max_intentos: Número máximo de reintentos.

    Returns:
        El resultado de la operación.

    Raises:
        OperationError: Si se agotan los reintentos.
    """
    ultimo_error = None
    for intento in range(1, max_intentos + 1):
        try:
            return operacion()
        except OperationError as exc:
            ultimo_error = exc
            print(f"  Intento {intento}/{max_intentos} fallido: {exc}")
            if intento < max_intentos:
                time.sleep(0.1)  # Espera breve antes de reintentar
    raise ultimo_error


# Escenario 1: Operación que falla permanentemente
print("=== Escenario 1: Fallo permanente ===")
cliente = RedisSimulado()
try:
    resultado = operacion_con_reintento(cliente, lambda: cliente.get("usuario:1"), max_intentos=3)
    print(f"Resultado: {resultado}")
except OperationError as exc:
    print(f"Error final tras agotar reintentos: {exc}")

# Escenario 2: Operación que se recupera
print("\n=== Escenario 2: Recuperación tras reintentos ===")
cliente2 = RedisSimulado()


# Simular que Redis se recupera tras el segundo intento
def get_con_recuperacion():
    cliente2._intentos += 0  # Ya cuenta internamente
    if cliente2._intentos >= 2:
        cliente2.simular_recuperacion()
    return cliente2.get("usuario:1")


try:
    resultado = operacion_con_reintento(cliente2, get_con_recuperacion, max_intentos=5)
    print(f"Resultado tras recuperación: {resultado}")
except OperationError as exc:
    print(f"Error final: {exc}")

# Escenario 3: Fallback a valor por defecto
print("\n=== Escenario 3: Fallback a valor por defecto ===")
cliente3 = RedisSimulado()
try:
    resultado = cliente3.get("config:tema")
except OperationError:
    resultado = "tema_claro"  # Valor por defecto
    print(f"Usando valor por defecto: {resultado}")
