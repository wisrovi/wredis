"""Validación de valores de bit (0 y 1) para operaciones SETBIT/GETBIT."""

from wredis._validation import validate_bit_value
from wredis._exceptions import ValidationError

# Valor de bit válido: 0
validate_bit_value(0)
print("Bit 0: válido")

# Valor de bit válido: 1
validate_bit_value(1)
print("Bit 1: válido")

# Valores inválidos para bit
valores_invalidos = [-1, 2, 3, 100, 999]

for valor in valores_invalidos:
    try:
        validate_bit_value(valor)
        print(f"Bit {valor}: válido (inesperado)")
    except ValidationError as e:
        print(f"Bit {valor}: inválido -> {e}")

print("\nSe demostró que solo 0 y 1 son valores válidos para bits.")
