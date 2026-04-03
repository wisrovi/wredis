"""Ejemplo 11: Reintento en operaciones por lotes (batch).

Demuestra como aplicar @retry a operaciones que procesan
multiples elementos en lote, reintentando el lote completo.
"""

import redis
from wredis._retry import retry
from wredis._exceptions import OperationError


class BatchProcessor:
    """Procesador de lotes con soporte de reintento."""

    def __init__(self) -> None:
        self._procesados: list[str] = []
        self._intentos = 0

    def procesar_lote(self, elementos: list[str]) -> list[str]:
        """Procesa un lote completo de elementos."""
        self._intentos += 1
        # Falla en el primer intento para demostrar reintento
        if self._intentos <= 1:
            raise redis.ConnectionError("Conexion perdida durante procesamiento")
        self._procesados.extend(elementos)
        return self._procesados


procesador = BatchProcessor()


@retry(max_attempts=3, delay=0.1, backoff=2.0)
def ejecutar_lote(elementos: list[str]) -> list[str]:
    """Ejecuta un lote de operaciones con reintento automatico."""
    return procesador.procesar_lote(elementos)


@retry(max_attempts=3, delay=0.1, backoff=2.0)
def ejecutar_lote_con_fallo_permanente(elementos: list[str]) -> list[str]:
    """Lote que siempre falla para demostrar el error final."""
    raise redis.TimeoutError("Servicio de lote permanentemente fuera de linea")


if __name__ == "__main__":
    print("=== Ejemplo 11: Operaciones por Lotes ===")

    # Lote exitoso tras reintento
    lote1 = ["item_1", "item_2", "item_3"]
    resultado = ejecutar_lote(lote1)
    print(f"Lote 1 procesado: {resultado}")

    # Segundo lote sin fallos
    lote2 = ["item_4", "item_5"]
    resultado2 = ejecutar_lote(lote2)
    print(f"Lote 2 procesado: {resultado2}")

    # Lote con fallo permanente
    try:
        ejecutar_lote_con_fallo_permanente(["item_x", "item_y"])
    except OperationError as e:
        print(f"Lote con fallo permanente: {e}")

    print(f"Total intentos del procesador: {procesador._intentos}")
