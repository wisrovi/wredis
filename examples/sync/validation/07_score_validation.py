"""Validación de scores para conjuntos ordenados (sorted sets)."""

from wredis._validation import validate_score
from wredis._exceptions import ValidationError

# Score entero positivo
validate_score(100)
print("Score 100: válido")

# Score entero negativo
validate_score(-50)
print("Score -50: válido")

# Score flotante
validate_score(3.14159)
print("Score 3.14159: válido")

# Score cero
validate_score(0)
print("Score 0: válido")

# Score flotante negativo
validate_score(-999.99)
print("Score -999.99: válido")

# Score NaN (inválido)
try:
    validate_score(float("nan"))
    print("Score NaN: válido (inesperado)")
except ValidationError as e:
    print(f"Score NaN: inválido -> {e}")

# Score infinito positivo (inválido)
try:
    validate_score(float("inf"))
    print("Score inf: válido (inesperado)")
except ValidationError as e:
    print(f"Score inf: inválido -> {e}")

# Score infinito negativo (inválido)
try:
    validate_score(float("-inf"))
    print("Score -inf: válido (inesperado)")
except ValidationError as e:
    print(f"Score -inf: inválido -> {e}")

print("\nSe demostró la validación de scores para conjuntos ordenados.")
