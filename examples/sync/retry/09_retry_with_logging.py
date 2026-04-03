"""Ejemplo 09: Reintento con logging y monitoreo.

Demuestra como agregar logging a las operaciones con retry para
monitorear los reintentos y diagnosticar problemas.
"""

import redis
from wredis._retry import retry
from wredis._exceptions import OperationError


class MonitorReintentos:
    """Monitor que registra estadisticas de reintentos."""

    def __init__(self) -> None:
        self.total_operaciones = 0
        self.total_reintentos = 0
        self.operaciones_exitosas = 0
        self.operaciones_fallidas = 0

    def registrar_operacion(self, nombre: str, exito: bool, reintentos: int) -> None:
        """Registra el resultado de una operacion."""
        self.total_operaciones += 1
        self.total_reintentos += reintentos
        if exito:
            self.operaciones_exitosas += 1
        else:
            self.operaciones_fallidas += 1
        print(f"  [LOG] {nombre}: {'EXITO' if exito else 'FALLO'} (reintentos: {reintentos})")

    def resumen(self) -> dict:
        """Devuelve estadisticas acumuladas."""
        return {
            "total_operaciones": self.total_operaciones,
            "total_reintentos": self.total_reintentos,
            "exitosas": self.operaciones_exitosas,
            "fallidas": self.operaciones_fallidas,
        }


monitor = MonitorReintentos()
fallas_simuladas = {"op_a": 1, "op_b": 0, "op_c": 5}  # op_c nunca tendra exito


def crear_operacion(nombre: str):
    """Factory para crear operaciones con monitoreo."""
    intentos = [0]

    @retry(max_attempts=4, delay=0.05, backoff=1.0)
    def operacion() -> str:
        intentos[0] += 1
        if intentos[0] <= fallas_simuladas.get(nombre, 0):
            raise redis.ConnectionError(f"Fallo simulado en {nombre}")
        return f"Resultado de {nombre}"

    return operacion, intentos


if __name__ == "__main__":
    print("=== Ejemplo 09: Logging y Monitoreo ===")

    operaciones = {
        "op_a": crear_operacion("op_a"),  # Falla 1 vez, luego exito
        "op_b": crear_operacion("op_b"),  # Sin fallos
        "op_c": crear_operacion("op_c"),  # Siempre falla
    }

    for nombre, (func, intentos_ref) in operaciones.items():
        try:
            resultado = func()
            monitor.registrar_operacion(nombre, True, intentos_ref[0] - 1)
            print(f"  Resultado: {resultado}")
        except OperationError:
            monitor.registrar_operacion(nombre, False, intentos_ref[0])

    print(f"\nResumen del monitor:")
    for clave, valor in monitor.resumen().items():
        print(f"  {clave}: {valor}")
