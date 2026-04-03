"""Validación de TTL con valores inválidos que lanzan ValidationError."""

from wredis._validation import validate_ttl
from wredis._exceptions import ValidationError

# Intentar validar un TTL negativo menor que -1 (inválido)
invalid_ttls = [-2, -10, -100, -999]

for ttl in invalid_ttls:
    try:
        validate_ttl(ttl)
        print(f"TTL {ttl}: válido (inesperado)")
    except ValidationError as e:
        print(f"TTL {ttl}: inválido -> {e}")

print("\nSe demostró que los TTL menores a -1 generan ValidationError.")
