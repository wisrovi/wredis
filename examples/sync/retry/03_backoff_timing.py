"""Ejemplo 03: Tiempo de backoff exponencial.

Demuestra como el parametro backoff multiplica el delay entre cada
reintento, creando pausas cada vez mas largas.
"""

import time
import redis
from wredis._retry import retry


# Registro de marcas de tiempo para medir los delays
marcas_tiempo: list[float] = []


@retry(max_attempts=5, delay=0.1, backoff=2.0)
def operacion_con_backoff() -> str:
    """Operacion que siempre falla para demostrar el backoff."""
    marcas_tiempo.append(time.time())
    raise redis.ConnectionError("Conexion rechazada")


if __name__ == "__main__":
    print("=== Ejemplo 03: Backoff Exponencial ===")

    try:
        operacion_con_backoff()
    except Exception as e:
        print(f"Error final: {e}")

    # Calcular los delays reales entre intentos
    print("\nTiempos entre intentos:")
    for i in range(1, len(marcas_tiempo)):
        delay_real = marcas_tiempo[i] - marcas_tiempo[i - 1]
        delay_esperado = 0.1 * (2.0 ** (i - 1))
        print(f"  Intento {i} -> {i + 1}: delay real={delay_real:.3f}s, delay esperado={delay_esperado:.3f}s")

    print(f"\nTotal de intentos: {len(marcas_tiempo)}")
