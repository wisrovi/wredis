"""Ejemplo 10: Reintento con decorador envoltorio (wrapper).

Muestra como crear un decorador personalizado que combina @retry
con logica adicional como validacion de entrada.
"""

import redis
from wredis._retry import retry
from wredis._exceptions import OperationError


def retry_con_validacion(
    max_attempts: int = 3,
    delay: float = 0.1,
    backoff: float = 2.0,
):
    """Decorador que combina validacion de entrada con reintento.

    Primero valida que los argumentos sean correctos, luego aplica
    el reintento automatico en caso de fallos de Redis.
    """

    def decorador(func):
        @retry(max_attempts=max_attempts, delay=delay, backoff=backoff)
        def wrapper(*args, **kwargs):
            # Validacion antes de ejecutar
            if args and isinstance(args[0], str) and not args[0].strip():
                raise ValueError("El argumento no puede estar vacio")
            return func(*args, **kwargs)

        return wrapper

    return decorador


# Simulamos un servicio de Redis
class RedisService:
    def __init__(self) -> None:
        self._datos: dict[str, str] = {}
        self._intentos = 0

    def guardar(self, clave: str, valor: str) -> bool:
        self._intentos += 1
        if self._intentos <= 1:
            raise redis.TimeoutError("Timeout en escritura")
        self._datos[clave] = valor
        return True

    def obtener(self, clave: str) -> str | None:
        return self._datos.get(clave)


servicio = RedisService()


@retry_con_validacion(max_attempts=3, delay=0.1, backoff=1.5)
def guardar_datos(clave: str, valor: str) -> bool:
    """Guarda datos con validacion previa y reintento."""
    return servicio.guardar(clave, valor)


@retry_con_validacion(max_attempts=3, delay=0.1, backoff=1.5)
def buscar_datos(clave: str) -> str | None:
    """Busca datos con validacion previa y reintento."""
    return servicio.obtener(clave)


if __name__ == "__main__":
    print("=== Ejemplo 10: Decorador Wrapper ===")

    # Operacion exitosa con reintento
    exito = guardar_datos("usuario:1", "Carlos")
    print(f"Guardado: {exito}")

    # Lectura sin fallos
    valor = buscar_datos("usuario:1")
    print(f"Valor encontrado: {valor}")

    # Validacion: clave vacia
    try:
        guardar_datos("", "valor")
    except ValueError as e:
        print(f"Validacion detecto error: {e}")

    print(f"Total intentos del servicio: {servicio._intentos}")
