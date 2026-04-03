"""Ejemplo 05: Reintento con operaciones de escritura en Redis.

Demuestra el uso de @retry para operaciones SET/HSET que pueden
fallar y necesitan reintentarse de forma segura.
"""

import redis
from wredis._retry import retry


class RedisWriteMock:
    """Mock de cliente Redis para operaciones de escritura."""

    def __init__(self) -> None:
        self._almacen: dict[str, str] = {}
        self._intentos = 0

    def set(self, clave: str, valor: str, ex: int | None = None) -> bool:
        self._intentos += 1
        if self._intentos <= 1:
            raise redis.TimeoutError("Tiempo de espera agotado en escritura")
        self._almacen[clave] = valor
        return True

    def get(self, clave: str) -> str | None:
        return self._almacen.get(clave)


cliente = RedisWriteMock()


@retry(max_attempts=3, delay=0.1, backoff=2.0)
def guardar_en_cache(clave: str, valor: str, ttl: int | None = None) -> bool:
    """Guarda un par clave-valor en Redis con reintento automatico."""
    return cliente.set(clave, valor, ex=ttl)


@retry(max_attempts=3, delay=0.1, backoff=2.0)
def guardar_hash(campo: str, valor: str) -> bool:
    """Guarda datos en un hash de Redis con reintento."""
    return cliente.set(f"hash:{campo}", valor)


if __name__ == "__main__":
    print("=== Ejemplo 05: Operaciones de Escritura Redis ===")

    # Guardar con reintento
    exito = guardar_en_cache("config:tema", "oscuro", ttl=3600)
    print(f"Guardado exitoso: {exito}")

    # Verificar que se guardo correctamente
    valor = cliente.get("config:tema")
    print(f"Valor almacenado: {valor}")

    # Guardar hash
    exito_hash = guardar_hash("nombre", "WRedis")
    print(f"Hash guardado: {exito_hash}")
    print(f"Valor hash: {cliente.get('hash:nombre')}")
