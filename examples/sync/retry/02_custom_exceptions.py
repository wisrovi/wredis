"""Ejemplo 02: Reintento con excepciones personalizadas.

Muestra como configurar el decorador @retry para capturar tipos de
excepciones distintos a los predeterminados de Redis.
"""

import redis
from wredis._retry import retry
from wredis._exceptions import OperationError


# Excepcion personalizada para simular un error de negocio
class ServicioNoDisponibleError(Exception):
    """Error cuando un servicio externo no esta disponible."""


# Excepcion para datos corruptos
class DatosCorruptosError(Exception):
    """Error cuando los datos recibidos estan corruptos."""


contador = 0


@retry(
    max_attempts=4,
    delay=0.05,
    backoff=1.0,
    exceptions=(ServicioNoDisponibleError, redis.TimeoutError),
)
def consultar_servicio() -> str:
    """Consulta un servicio que puede fallar por indisponibilidad."""
    global contador
    contador += 1
    if contador <= 2:
        raise ServicioNoDisponibleError("Servicio temporalmente fuera de linea")
    return "Datos obtenidos correctamente"


if __name__ == "__main__":
    print("=== Ejemplo 02: Excepciones Personalizadas ===")

    # Esta funcion tiene exito despues de 2 reintentos
    resultado = consultar_servicio()
    print(f"Resultado: {resultado}")
    print(f"Intentos realizados: {contador}")

    # Esta funcion siempre falla con una excepcion NO configurada
    @retry(max_attempts=2, delay=0.05, backoff=1.0, exceptions=(redis.ConnectionError,))
    def operacion_con_datos_corruptos() -> str:
        """Operacion que falla con excepcion no capturada por retry."""
        raise DatosCorruptosError("Los datos estan corruptos")

    try:
        operacion_con_datos_corruptos()
    except DatosCorruptosError as e:
        print(f"Excepcion no capturada por retry (como se esperaba): {e}")
