"""Ejemplo 12: Reintento con cache local como fallback.

Implementa un patron donde si Redis falla despues de todos los
reintentos, se usa una cache local como respaldo.
"""

import redis
from wredis._retry import retry
from wredis._exceptions import OperationError


class CacheConFallback:
    """Cache que usa Redis con fallback a memoria local."""

    def __init__(self) -> None:
        self._cache_local: dict[str, str] = {"config:app": "v1.0"}
        self._intentos_redis = 0

    def _leer_redis(self, clave: str) -> str | None:
        """Simula lectura de Redis (siempre falla)."""
        self._intentos_redis += 1
        raise redis.ConnectionError("Redis no disponible")

    @retry(max_attempts=3, delay=0.05, backoff=1.0)
    def obtener_con_reintento(self, clave: str) -> str | None:
        """Intenta leer de Redis con reintentos."""
        return self._leer_redis(clave)

    def obtener(self, clave: str) -> str | None:
        """Obtiene dato de Redis o fallback a cache local."""
        try:
            return self.obtener_con_reintento(clave)
        except OperationError:
            print(f"  [FALLBACK] Redis fallo, usando cache local para '{clave}'")
            return self._cache_local.get(clave)


cache = CacheConFallback()


if __name__ == "__main__":
    print("=== Ejemplo 12: Cache con Fallback ===")

    # Clave que existe en cache local
    valor = cache.obtener("config:app")
    print(f"Valor obtenido: {valor}")

    # Clave que no existe en ningun lado
    valor_faltante = cache.obtener("config:inexistente")
    print(f"Valor inexistente: {valor_faltante}")

    print(f"Total intentos a Redis: {cache._intentos_redis}")
