"""Validación de casos límite (edge cases) para todas las funciones."""

from wredis._validation import validate_ttl, validate_key, validate_offset, validate_bit_value, validate_score
from wredis._exceptions import ValidationError

print("=== Casos límite para TTL ===")
# Límite inferior válido
validate_ttl(-1)
print("TTL -1 (límite inferior): válido")

# Límite inferior inválido
try:
    validate_ttl(-2)
except ValidationError:
    print("TTL -2 (justo debajo del límite): inválido")

print("\n=== Casos límite para Key ===")
# Clave de exactamente 512 caracteres
validate_key("a" * 512)
print("Clave de 512 chars (límite exacto): válida")

# Clave de 513 caracteres (un carácter más)
try:
    validate_key("a" * 513)
except ValidationError:
    print("Clave de 513 chars (uno más del límite): inválida")

print("\n=== Casos límite para Offset ===")
validate_offset(0)
print("Offset 0 (límite inferior): válido")

try:
    validate_offset(-1)
except ValidationError:
    print("Offset -1 (justo debajo del límite): inválido")

print("\n=== Casos límite para Bit Value ===")
validate_bit_value(0)
validate_bit_value(1)
print("Bit 0 y 1: válidos")

try:
    validate_bit_value(-1)
except ValidationError:
    print("Bit -1: inválido")

try:
    validate_bit_value(2)
except ValidationError:
    print("Bit 2: inválido")

print("\n=== Casos límite para Score ===")
validate_score(0)
print("Score 0: válido")

# Score muy grande pero finito
validate_score(1e308)
print("Score 1e308: válido")

try:
    validate_score(float("nan"))
except ValidationError:
    print("Score NaN: inválido")

try:
    validate_score(float("inf"))
except ValidationError:
    print("Score inf: inválido")

print("\nTodos los casos límite fueron verificados correctamente.")
