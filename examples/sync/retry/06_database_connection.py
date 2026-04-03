"""Ejemplo 06: Reintento en conexiones a base de datos Redis.

Muestra como usar @retry para establecer conexiones a Redis de forma
resiliente ante fallos temporales de red.
"""

import redis
from wredis._retry import retry
from wredis._exceptions import OperationError


class GestorConexion:
    """Gestor de conexiones Redis con reintento integrado."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self._conexion: redis.Redis | None = None
        self._intentos_conexion = 0

    @retry(max_attempts=4, delay=0.1, backoff=2.0)
    def conectar(self) -> redis.Redis:
        """Establece conexion a Redis con reintentos automaticos."""
        self._intentos_conexion += 1
        if self._intentos_conexion < 3:
            raise redis.ConnectionError(f"No se pudo conectar a {self.host}:{self.port}")
        # Simulamos conexion exitosa
        self._conexion = redis.Redis(host=self.host, port=self.port)
        return self._conexion

    @retry(max_attempts=3, delay=0.05, backoff=1.5)
    def verificar_conexion(self) -> bool:
        """Verifica que la conexion este activa con ping."""
        if self._intentos_conexion < 3:
            raise redis.ConnectionError("Conexion inestable")
        return True


if __name__ == "__main__":
    print("=== Ejemplo 06: Conexion a Base de Datos ===")

    gestor = GestorConexion("localhost", 6379)

    # Conectar con reintentos
    conexion = gestor.conectar()
    print(f"Conexion establecida: {conexion}")

    # Verificar conexion
    activo = gestor.verificar_conexion()
    print(f"Conexion activa: {activo}")
    print(f"Total intentos de conexion: {gestor._intentos_conexion}")
