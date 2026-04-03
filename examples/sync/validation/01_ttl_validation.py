"""Validación básica de TTL con valores aceptables."""

from wredis._validation import validate_ttl
from wredis._exceptions import ValidationError

# TTL positivo válido: la clave expira en 3600 segundos (1 hora)
validate_ttl(3600)
print("TTL 3600: válido")

# TTL igual a 0 también es válido (expira inmediatamente)
validate_ttl(0)
print("TTL 0: válido")

# TTL igual a -1 indica que la clave nunca expira
validate_ttl(-1)
print("TTL -1: válido (sin expiración)")

print("\nTodos los valores de TTL válidos fueron aceptados correctamente.")
