"""Validación de múltiples campos en una sola operación (validación por lotes)."""

from wredis._validation import validate_ttl, validate_key, validate_offset, validate_bit_value, validate_score
from wredis._exceptions import ValidationError


def validar_operacion_bitmap(key: str, offset: int, bit_value: int) -> bool:
    """Valida todos los parámetros de una operación con bitmap."""
    errores = []

    # Validar cada campo individualmente
    try:
        validate_key(key)
    except ValidationError as e:
        errores.append(str(e))

    try:
        validate_offset(offset)
    except ValidationError as e:
        errores.append(str(e))

    try:
        validate_bit_value(bit_value)
    except ValidationError as e:
        errores.append(str(e))

    return errores


# Caso válido: todos los parámetros correctos
errores = validar_operacion_bitmap("usuario:flags", 0, 1)
if errores:
    print(f"Errores: {errores}")
else:
    print("Operación bitmap válida: key='usuario:flags', offset=0, bit=1")

# Caso inválido: múltiples errores
errores = validar_operacion_bitmap("", -5, 3)
if errores:
    print(f"Operación inválida con {len(errores)} errores:")
    for error in errores:
        print(f"  - {error}")

# Caso parcialmente inválido: solo el bit es incorrecto
errores = validar_operacion_bitmap("usuario:flags", 100, 2)
if errores:
    print(f"Operación con 1 error: {errores[0]}")

print("\nSe demostró la validación por lotes de múltiples parámetros.")
