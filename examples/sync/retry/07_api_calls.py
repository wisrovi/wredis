"""Ejemplo 07: Reintento en llamadas a API externas.

Demuestra como usar @retry para llamadas a APIs HTTP que pueden
fallar por timeouts o errores de conexion.
"""

import redis
from wredis._retry import retry
from wredis._exceptions import OperationError


class APIMock:
    """Mock de cliente API para demostracion."""

    def __init__(self) -> None:
        self._intentos = 0
        self._datos = {"temperatura": 25.5, "humedad": 60}

    def obtener_datos_clima(self, ciudad: str) -> dict:
        """Simula llamada a API de clima con fallos intermitentes."""
        self._intentos += 1
        if self._intentos <= 2:
            raise redis.TimeoutError("Timeout al conectar con API externa")
        return {"ciudad": ciudad, **self._datos}

    def enviar_notificacion(self, mensaje: str) -> bool:
        """Simula envio de notificacion con fallos."""
        self._intentos += 1
        if self._intentos <= 3:
            raise redis.ConnectionError("Error de conexion con servicio de notificaciones")
        return True


api = APIMock()


@retry(max_attempts=3, delay=0.1, backoff=2.0)
def consultar_clima(ciudad: str) -> dict:
    """Consulta datos climaticos con reintento automatico."""
    return api.obtener_datos_clima(ciudad)


@retry(max_attempts=5, delay=0.05, backoff=1.5)
def enviar_alerta(mensaje: str) -> bool:
    """Envia alerta con mas intentos para mayor resiliencia."""
    return api.enviar_notificacion(mensaje)


if __name__ == "__main__":
    print("=== Ejemplo 07: Llamadas a API Externas ===")

    # Consulta de clima con reintentos
    clima = consultar_clima("Buenos Aires")
    print(f"Clima en {clima['ciudad']}: {clima['temperatura']}C, {clima['humedad']}% humedad")

    # Envio de notificacion
    enviado = enviar_alerta("Alerta de sistema")
    print(f"Notificacion enviada: {enviado}")
    print(f"Total intentos de API: {api._intentos}")
