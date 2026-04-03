"""Validación de scores con diferentes tipos numéricos de Python."""

from wredis._validation import validate_score
from wredis._exceptions import ValidationError

# Entero positivo
validate_score(42)
print("int positivo (42): válido")

# Entero negativo
validate_score(-42)
print("int negativo (-42): válido")

# Entero cero
validate_score(0)
print("int cero (0): válido")

# Float positivo
validate_score(3.14)
print("float positivo (3.14): válido")

# Float negativo
validate_score(-2.718)
print("float negativo (-2.718): válido")

# Booleano: en Python bool es subclase de int, así que True=1 y False=0 son válidos
validate_score(True)
print("bool True (equivale a 1): válido")

validate_score(False)
print("bool False (equivale a 0): válido")

# Tipo inválido: string
try:
    validate_score("100")
    print("str '100': válido (inesperado)")
except ValidationError as e:
    print(f"str '100': inválido -> {e}")

# Tipo inválido: None
try:
    validate_score(None)
    print("None: válido (inesperado)")
except ValidationError as e:
    print(f"None: inválido -> {e}")

# Tipo inválido: lista
try:
    validate_score([1, 2, 3])
    print("lista: válido (inesperado)")
except ValidationError as e:
    print(f"lista: inválido -> {e}")

print("\nSe demostró la validación de scores con diferentes tipos numéricos.")
