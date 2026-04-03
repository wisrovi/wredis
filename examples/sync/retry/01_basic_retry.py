"""Ejemplo 01: Uso basico del decorador retry.

Demuestra como el decorador @retry reintenta automaticamente una funcion
que falla con redis.ConnectionError hasta agotar los intentos configurados.
"""

import redis
from wredis._retry import retry


# Funcion simulada que falla las primeras 2 veces
intentos = 0


@retry(max_attempts=3, delay=0.1, backoff=1.0)
def operacion_inestable() -> str:
    """Simula una operacion que falla intermitentemente."""
    global intentos
    intentos += 1
    if intentos < 3:
        raise redis.ConnectionError("Conexion intermitente perdida")
    return "Operacion exitosa en el intento 3"


if __name__ == "__main__":
    print("=== Ejemplo 01: Retry Basico ===")
    resultado = operacion_inestable()
    print(f"Resultado: {resultado}")
    print(f"Total de intentos realizados: {intentos}")
