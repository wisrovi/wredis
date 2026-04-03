"""Validación de offset para operaciones con bitmaps."""

from wredis._validation import validate_offset
from wredis._exceptions import ValidationError

# Offset cero: primer bit del bitmap
validate_offset(0)
print("Offset 0: válido")

# Offset positivo pequeño
validate_offset(42)
print("Offset 42: válido")

# Offset grande (dentro de un bitmap extenso)
validate_offset(1000000)
print("Offset 1000000: válido")

# Offset negativo (caso inválido)
try:
    validate_offset(-1)
    print("Offset -1: válido (inesperado)")
except ValidationError as e:
    print(f"Offset -1: inválido -> {e}")

print("\nSe demostró la validación de offsets para bitmaps.")
