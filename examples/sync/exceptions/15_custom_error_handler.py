"""Demostración de creación de manejadores de error personalizados.

Muestra cómo diseñar clases y funciones para manejar excepciones
de WRedis de forma centralizada y reutilizable.
"""

from wredis._exceptions import (
    CacheError,
    ClusterError,
    OperationError,
    PubSubError,
    QueueError,
    RedisConnectionError,
    SentinelError,
    SerializationError,
    StreamError,
    TransactionError,
    ValidationError,
    WRedisError,
)


class GestorDeErroresWRedis:
    """Manejador centralizado de excepciones de WRedis.

    Permite registrar callbacks para cada tipo de error y
    ejecutar acciones específicas automáticamente.
    """

    def __init__(self):
        self._manejadores = {}
        self._manejador_por_defecto = None
        self._historial = []

    def registrar(self, tipo_error, manejador):
        """Registra un manejador para un tipo de error.

        Args:
            tipo_error: Clase de excepción a manejar.
            manejador: Función que recibe la excepción y retorna un valor.
        """
        self._manejadores[tipo_error] = manejador

    def registrar_por_defecto(self, manejador):
        """Registra un manejador para errores no registrados.

        Args:
            manejador: Función manejadora por defecto.
        """
        self._manejador_por_defecto = manejador

    def manejar(self, exc):
        """Ejecuta el manejador correspondiente a una excepción.

        Args:
            exc: La excepción capturada.

        Returns:
            El resultado del manejador o None.
        """
        self._historial.append(exc)
        manejador = self._manejadores.get(type(exc))
        if manejador is None:
            # Buscar manejador para clases padre
            for tipo_err, handler in self._manejadores.items():
                if isinstance(exc, tipo_err):
                    manejador = handler
                    break
        if manejador is None:
            manejador = self._manejador_por_defecto
        if manejador:
            return manejador(exc)
        return None

    @property
    def historial(self):
        return list(self._historial)


# Configurar el gestor
gestor = GestorDeErroresWRedis()

# Registrar manejadores específicos
gestor.registrar(
    RedisConnectionError,
    lambda exc: f"[RECONECTAR] {exc} - Intentando reconexión...",
)
gestor.registrar(
    ValidationError,
    lambda exc: f"[VALIDAR] {exc} - Solicitando datos corregidos",
)
gestor.registrar(
    SerializationError,
    lambda exc: f"[SERIALIZAR] {exc} - Usando serializador alternativo",
)
gestor.registrar(
    TransactionError,
    lambda exc: f"[REINTENTAR] {exc} - Reintentando transacción",
)
gestor.registrar(
    QueueError,
    lambda exc: f"[COLA] {exc} - Descartando mensaje antiguo",
)

# Manejador por defecto
gestor.registrar_por_defecto(lambda exc: f"[GENÉRICO] {type(exc).__name__}: {exc}")


# Simular operaciones y manejar errores
def simular_error(tipo):
    raise tipo(f"Error simulado de {tipo.__name__}")


errores_a_probar = [
    RedisConnectionError,
    ValidationError,
    SerializationError,
    TransactionError,
    QueueError,
    CacheError,
    PubSubError,
    StreamError,
]

print("=== Manejadores de error personalizados ===\n")

for tipo in errores_a_probar:
    try:
        simular_error(tipo)
    except WRedisError as exc:
        resultado = gestor.manejar(exc)
        print(f"  {resultado}")

# Mostrar historial
print(f"\n=== Historial de errores ({len(gestor.historial)}) ===")
for i, err in enumerate(gestor.historial, 1):
    print(f"  {i}. {type(err).__name__}: {err}")


# Patrón de decorador para manejo automático
print("\n=== Decorador @manejar_errores ===")


def manejar_errores(manejador):
    """Decorador que captura WRedisError y lo pasa al manejador.

    Args:
        manejador: Función que recibe (exc, func_name, args, kwargs).

    Returns:
        Decorador.
    """

    def decorador(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except WRedisError as exc:
                return manejador(exc, func.__name__, args, kwargs)

        return wrapper

    return decorador


def mi_manejador(exc, nombre_func, args, kwargs):
    return f"Error en {nombre_func}: {type(exc).__name__} - {exc}"


@manejar_errores(mi_manejador)
def obtener_usuario(user_id):
    if user_id < 0:
        raise ValidationError(f"ID inválido: {user_id}")
    return {"id": user_id}


@manejar_errores(mi_manejador)
def conectar_redis():
    raise RedisConnectionError("Servidor no disponible")


print(obtener_usuario(-1))
print(conectar_redis())
print(obtener_usuario(42))  # Caso exitoso
