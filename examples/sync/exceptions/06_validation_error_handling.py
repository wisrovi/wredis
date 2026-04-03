"""Demostración de manejo de ValidationError.

Muestra cómo usar ValidationError para validar datos antes de
enviarlos a Redis y manejar los errores de validación.
"""

from wredis._exceptions import ValidationError


def validar_clave_redis(clave):
    """Valida que una clave de Redis cumpla las reglas básicas.

    Args:
        clave: La clave a validar.

    Raises:
        ValidationError: Si la clave no es válida.
    """
    if not clave:
        raise ValidationError("La clave no puede estar vacía")
    if not isinstance(clave, str):
        raise ValidationError(f"La clave debe ser str, no {type(clave).__name__}")
    if len(clave) > 512:
        raise ValidationError(f"La clave excede 512 caracteres (tiene {len(clave)})")
    if " " in clave:
        raise ValidationError("La clave no puede contener espacios")
    return True


def validar_valor_para_set(clave, valor):
    """Valida un par clave-valor antes de un SET.

    Args:
        clave: La clave de Redis.
        valor: El valor a almacenar.

    Raises:
        ValidationError: Si la validación falla.
    """
    validar_clave_redis(clave)
    if valor is None:
        raise ValidationError(f"No se puede almacenar None en '{clave}'")


# Caso 1: Clave vacía
try:
    validar_clave_redis("")
except ValidationError as exc:
    print(f"Error de validación: {exc}")

# Caso 2: Clave con espacios
try:
    validar_clave_redis("mi clave con espacios")
except ValidationError as exc:
    print(f"Error de validación: {exc}")

# Caso 3: Tipo incorrecto
try:
    validar_clave_redis(12345)
except ValidationError as exc:
    print(f"Error de validación: {exc}")

# Caso 4: Valor None
try:
    validar_valor_para_set("usuario:1", None)
except ValidationError as exc:
    print(f"Error de validación: {exc}")

# Caso 5: Validación exitosa
try:
    validar_valor_para_set("usuario:1", {"nombre": "Ana"})
    print("Validación exitosa: clave y valor son correctos")
except ValidationError as exc:
    print(f"Error de validación: {exc}")

# Caso 6: Clave demasiado larga
try:
    validar_clave_redis("a" * 600)
except ValidationError as exc:
    print(f"Error de validación: {exc}")
