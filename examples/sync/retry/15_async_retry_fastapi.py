"""Ejemplo 15: Async retry integrado con FastAPI.

Demuestra como usar async_retry en endpoints de FastAPI para
crear APIs resilientes ante fallos de Redis.
"""

import asyncio
import redis
from wredis._retry import async_retry
from wredis._exceptions import OperationError


# Simulamos FastAPI sin necesidad de instalarlo
class FastAPIMock:
    """Mock minimalista de FastAPI para demostracion."""

    def __init__(self) -> None:
        self.rutas: dict[str, callable] = {}

    def get(self, path: str):
        """Decorador para registrar rutas GET."""

        def decorador(func):
            self.rutas[path] = func
            return func

        return decorador

    async def ejecutar(self, path: str, **kwargs) -> dict:
        """Ejecuta una ruta simulando una peticion HTTP."""
        # Busca la ruta coincidente (soporta parametros tipo {param})
        ruta_encontrada = None
        for ruta_registrada, func in self.rutas.items():
            partes_registradas = ruta_registrada.split("/")
            partes_path = path.split("/")
            if len(partes_registradas) == len(partes_path):
                coincide = True
                params = {}
                for i, parte_reg in enumerate(partes_registradas):
                    if parte_reg.startswith("{") and parte_reg.endswith("}"):
                        # Es un parametro, extraer nombre y valor
                        param_name = parte_reg[1:-1]
                        params[param_name] = partes_path[i]
                    elif parte_reg != partes_path[i]:
                        coincide = False
                        break
                if coincide:
                    ruta_encontrada = (func, params)
                    break

        if ruta_encontrada is None:
            return {"error": "404 Not Found"}

        func, params = ruta_encontrada
        try:
            resultado = await func(**params, **kwargs)
            return {"status": 200, "data": resultado}
        except OperationError as e:
            return {"status": 503, "error": str(e)}


app = FastAPIMock()


class RedisClientMock:
    """Mock de cliente Redis para FastAPI."""

    def __init__(self) -> None:
        self._datos = {"usuario:1": {"nombre": "Ana", "rol": "admin"}}
        self._intentos = 0

    async def get_usuario(self, user_id: str) -> dict | None:
        self._intentos += 1
        if self._intentos <= 1:
            raise redis.ConnectionError("Redis desconectado")
        return self._datos.get(f"usuario:{user_id}")

    async def guardar_metrica(self, metrica: str, valor: float) -> bool:
        self._intentos += 1
        if self._intentos <= 2:
            raise redis.TimeoutError("Timeout al guardar metrica")
        return True


redis_client = RedisClientMock()


@app.get("/usuarios/{user_id}")
@async_retry(max_attempts=3, delay=0.1, backoff=2.0)
async def obtener_usuario(user_id: str) -> dict:
    """Endpoint para obtener usuario con reintento automatico."""
    usuario = await redis_client.get_usuario(user_id)
    if usuario is None:
        return {"error": "Usuario no encontrado"}
    return usuario


@app.get("/metricas")
@async_retry(max_attempts=4, delay=0.05, backoff=1.5)
async def registrar_metrica() -> bool:
    """Endpoint para registrar metrica con reintento."""
    return await redis_client.guardar_metrica("requests", 1.0)


async def main() -> None:
    """Simula peticiones HTTP a la API."""
    print("=== Ejemplo 15: Async Retry con FastAPI ===")

    # Peticion para obtener usuario
    print("\nGET /usuarios/1")
    respuesta = await app.ejecutar("/usuarios/1")
    print(f"  Status: {respuesta['status']}")
    if "data" in respuesta:
        print(f"  Datos: {respuesta['data']}")
    else:
        print(f"  Error: {respuesta.get('error')}")

    # Peticion para registrar metrica
    print("\nGET /metricas")
    respuesta_metrica = await app.ejecutar("/metricas")
    print(f"  Status: {respuesta_metrica['status']}")
    print(f"  Datos: {respuesta_metrica.get('data')}")

    print(f"\nTotal intentos de Redis: {redis_client._intentos}")


if __name__ == "__main__":
    asyncio.run(main())
