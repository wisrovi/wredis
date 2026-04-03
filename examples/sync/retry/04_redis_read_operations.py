"""Ejemplo 04: Reintento con operaciones de lectura de Redis.

Muestra como usar @retry para operaciones GET de Redis que pueden
fallar por problemas temporales de conexion.
"""

import redis
from wredis._retry import retry


# Simulamos un cliente Redis que falla las primeras veces
class RedisMock:
    """Mock de cliente Redis para demostracion."""

    def __init__(self) -> None:
        self._datos: dict[str, str] = {"usuario:1": "Juan", "usuario:2": "Maria"}
        self._intentos = 0

    def get(self, key: str) -> str | None:
        self._intentos += 1
        if self._intentos <= 2:
            raise redis.ConnectionError("Conexion perdida temporalmente")
        return self._datos.get(key)

    @property
    def intentos(self) -> int:
        return self._intentos


cliente = RedisMock()


@retry(max_attempts=3, delay=0.1, backoff=1.5)
def obtener_valor(clave: str) -> str | None:
    """Obtiene un valor de Redis con reintento automatico."""
    return cliente.get(clave)


if __name__ == "__main__":
    print("=== Ejemplo 04: Operaciones de Lectura Redis ===")

    valor = obtener_valor("usuario:1")
    print(f"Valor obtenido para 'usuario:1': {valor}")
    print(f"Intentos necesarios: {cliente.intentos}")

    # Prueba con clave que no existe
    cliente._intentos = 0
    valor_inexistente = obtener_valor("usuario:99")
    print(f"Valor para 'usuario:99': {valor_inexistente}")
