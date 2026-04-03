"""Ejemplo 08: Patron circuit breaker con retry.

Implementa un circuit breaker simple que deja de reintentar cuando
se detectan demasiados fallos consecutivos.
"""

import redis
from wredis._retry import retry
from wredis._exceptions import OperationError


class CircuitBreaker:
    """Circuit breaker simple para proteger contra fallos repetidos."""

    def __init__(self, max_fallos: int = 5) -> None:
        self.max_fallos = max_fallos
        self.fallos_consecutivos = 0
        self.abierto = False

    def registrar_exito(self) -> None:
        """Registra una operacion exitosa y resetea el contador."""
        self.fallos_consecutivos = 0
        self.abierto = False

    def registrar_fallo(self) -> None:
        """Registra un fallo y abre el circuito si se supera el limite."""
        self.fallos_consecutivos += 1
        if self.fallos_consecutivos >= self.max_fallos:
            self.abierto = True
            print(f"  [CIRCUIT BREAKER] Circuito ABIERTO tras {self.fallos_consecutivos} fallos")

    def verificar(self) -> None:
        """Verifica si el circuito esta abierto antes de ejecutar."""
        if self.abierto:
            raise OperationError("Circuit breaker abierto: servicio no disponible")


# Instancia global del circuit breaker
cb = CircuitBreaker(max_fallos=3)
contador_llamadas = 0


@retry(max_attempts=3, delay=0.05, backoff=1.0)
def operacion_protegida() -> str:
    """Operacion protegida por circuit breaker."""
    cb.verificar()

    global contador_llamadas
    contador_llamadas += 1

    # Simulamos fallo permanente
    raise redis.ConnectionError("Servicio no responde")


if __name__ == "__main__":
    print("=== Ejemplo 08: Circuit Breaker ===")

    # Primera llamada: falla, el retry reintenta
    try:
        operacion_protegida()
    except OperationError as e:
        print(f"Error tras reintentos: {e}")
        cb.registrar_fallo()

    # Segunda llamada: el circuit breaker aun permite
    try:
        operacion_protegida()
    except OperationError as e:
        print(f"Error tras reintentos: {e}")
        cb.registrar_fallo()

    # Tercera llamada: abre el circuit breaker
    try:
        operacion_protegida()
    except OperationError as e:
        print(f"Error tras reintentos: {e}")
        cb.registrar_fallo()

    # Cuarta llamada: el circuit breaker bloquea inmediatamente
    print(f"\nEstado del circuit breaker: {'ABIERTO' if cb.abierto else 'CERRADO'}")
    print(f"Fallos consecutivos: {cb.fallos_consecutivos}")
    print(f"Total llamadas ejecutadas: {contador_llamadas}")
