"""Validación de parámetros para operaciones con bitmaps."""

from wredis._validation import validate_key, validate_offset, validate_bit_value
from wredis._exceptions import ValidationError


def simular_setbit(key: str, offset: int, value: int) -> dict:
    """Simula una operación SETBIT con validación completa."""
    # Validar cada parámetro individualmente
    validate_key(key)
    validate_offset(offset)
    validate_bit_value(value)

    return {"key": key, "offset": offset, "value": value, "status": "ok"}


print("=== Operaciones SETBIT válidas ===")

# Establecer el primer bit en 1
resultado = simular_setbit("usuario:1:permisos", 0, 1)
print(f"  {resultado}")

# Establecer un bit lejano en 0
resultado = simular_setbit("usuario:1:permisos", 1024, 0)
print(f"  {resultado}")

# Establecer bit en offset grande
resultado = simular_setbit("analytics:daily:2024", 50000, 1)
print(f"  {resultado}")

print("\n=== Operaciones SETBIT inválidas ===")

# Clave vacía
try:
    simular_setbit("", 0, 1)
except ValidationError as e:
    print(f"  Clave vacía: {e}")

# Offset negativo
try:
    simular_setbit("usuario:1:permisos", -1, 1)
except ValidationError as e:
    print(f"  Offset negativo: {e}")

# Valor de bit inválido
try:
    simular_setbit("usuario:1:permisos", 0, 2)
except ValidationError as e:
    print(f"  Valor de bit inválido: {e}")

# Múltiples errores
try:
    simular_setbit("", -5, 3)
except ValidationError as e:
    print(f"  Múltiples errores (primero detectado): {e}")

print("\nSe demostró la validación completa para operaciones con bitmaps.")
