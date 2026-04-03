"""Ejemplo 14: Reintento con decorador async_retry.

Muestra el uso de async_retry para funciones async/await con
reintento automatico usando asyncio.sleep.
"""

import asyncio
import redis
from wredis._retry import async_retry
from wredis._exceptions import OperationError


class ServicioAsyncMock:
    """Mock de servicio async para demostracion."""

    def __init__(self) -> None:
        self._intentos = 0

    async def consultar(self, recurso: str) -> dict:
        """Simula consulta async con fallos intermitentes."""
        self._intentos += 1
        await asyncio.sleep(0.01)  # Simula latencia de red
        if self._intentos <= 2:
            raise redis.TimeoutError("Timeout en consulta async")
        return {"recurso": recurso, "datos": "informacion obtenida"}


servicio = ServicioAsyncMock()


@async_retry(max_attempts=4, delay=0.1, backoff=2.0)
async def obtener_recurso(recurso: str) -> dict:
    """Obtiene un recurso con reintento async."""
    return await servicio.consultar(recurso)


@async_retry(max_attempts=3, delay=0.05, backoff=1.5)
async def operacion_que_falla() -> str:
    """Operacion async que siempre falla."""
    raise redis.ConnectionError("Conexion async perdida")


async def main() -> None:
    """Funcion principal async."""
    print("=== Ejemplo 14: Async Retry ===")

    # Operacion exitosa tras reintentos
    resultado = await obtener_recurso("usuarios")
    print(f"Resultado: {resultado}")
    print(f"Intentos realizados: {servicio._intentos}")

    # Operacion que falla permanentemente
    try:
        await operacion_que_falla()
    except OperationError as e:
        print(f"Error async tras reintentos: {e}")


if __name__ == "__main__":
    asyncio.run(main())
