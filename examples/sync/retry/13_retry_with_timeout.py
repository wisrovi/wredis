"""Ejemplo 13: Reintento con timeout maximo.

Demuestra como limitar el tiempo total de reintentos para evitar
que una operacion bloquee el programa indefinidamente.
"""

import time
import redis
from wredis._retry import retry
from wredis._exceptions import OperationError


class OperacionConTimeout:
    """Operacion que respeta un timeout maximo total."""

    def __init__(self, timeout_total: float) -> None:
        self.timeout_total = timeout_total
        self._inicio: float = 0
        self._intentos = 0

    def verificar_timeout(self) -> None:
        """Verifica si se excedio el timeout total."""
        transcurrido = time.time() - self._inicio
        if transcurrido > self.timeout_total:
            raise TimeoutError(f"Timeout de {self.timeout_total}s excedido (transcurrido: {transcurrido:.2f}s)")

    @retry(max_attempts=10, delay=0.2, backoff=1.5)
    def ejecutar(self) -> str:
        """Ejecuta operacion con verificacion de timeout."""
        self._intentos += 1
        self.verificar_timeout()
        raise redis.ConnectionError("Servicio no responde")


if __name__ == "__main__":
    print("=== Ejemplo 13: Reintento con Timeout ===")

    # Timeout corto: se detiene antes de agotar todos los intentos
    op_corta = OperacionConTimeout(timeout_total=0.5)
    op_corta._inicio = time.time()

    try:
        op_corta.ejecutar()
    except TimeoutError as e:
        print(f"Timeout detectado: {e}")
    except OperationError as e:
        print(f"Error de operacion: {e}")

    print(f"Intentos realizados antes del timeout: {op_corta._intentos}")

    # Timeout largo: permite mas reintentos
    print("\n--- Con timeout mas largo ---")
    op_larga = OperacionConTimeout(timeout_total=2.0)
    op_larga._inicio = time.time()

    try:
        op_larga.ejecutar()
    except TimeoutError as e:
        print(f"Timeout detectado: {e}")
    except OperationError as e:
        print(f"Error de operacion (agoto intentos): {e}")

    print(f"Intentos realizados: {op_larga._intentos}")
