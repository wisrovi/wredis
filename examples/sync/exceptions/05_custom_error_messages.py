"""Demostración de mensajes de error personalizados en excepciones.

Muestra cómo crear y lanzar excepciones de WRedis con mensajes
detallados y atributos adicionales para diagnóstico.
"""

from wredis._exceptions import (
    OperationError,
    ValidationError,
    WRedisError,
)


# Lanzar excepciones con mensajes descriptivos
try:
    raise ValidationError("El campo 'email' no tiene un formato válido: 'usuario@'")
except ValidationError as exc:
    print(f"Validación fallida: {exc}")


# Crear excepciones con contexto adicional usando args
try:
    error = OperationError("No se pudo ejecutar GET")
    error.clave = "usuario:1234"
    error.operacion = "GET"
    raise error
except OperationError as exc:
    print(f"\nOperación: {exc.operacion}")
    print(f"Clave afectada: {exc.clave}")
    print(f"Mensaje original: {exc}")


# Subclase con atributos personalizados para mejor diagnóstico
class ErrorConContexto(WRedisError):
    """Excepción que almacena contexto adicional para debugging.

    Attributes:
        operacion: Nombre de la operación que falló.
        detalles: Diccionario con información contextual.
    """

    def __init__(self, mensaje, operacion=None, detalles=None):
        super().__init__(mensaje)
        self.operacion = operacion
        self.detalles = detalles or {}

    def __str__(self):
        base = super().__str__()
        if self.detalles:
            detalles_str = ", ".join(f"{k}={v}" for k, v in self.detalles.items())
            return f"{base} [{detalles_str}]"
        return base


try:
    raise ErrorConContexto(
        "Tiempo de espera agotado",
        operacion="HGETALL",
        detalles={"clave": "sesion:abc", "timeout": "5s", "intentos": 3},
    )
except ErrorConContexto as exc:
    print(f"\nError con contexto: {exc}")
    print(f"  Operación: {exc.operacion}")
    print(f"  Detalles: {exc.detalles}")


# Formatear mensajes dinámicamente
clave = "producto:999"
valor = {"nombre": "Widget", "precio": None}

try:
    raise ValidationError(f"No se puede serializar el valor para '{clave}': el campo 'precio' no puede ser null")
except ValidationError as exc:
    print(f"\n{exc}")
