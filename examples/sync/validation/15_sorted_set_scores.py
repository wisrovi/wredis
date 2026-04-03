"""Validación de scores para operaciones con conjuntos ordenados (sorted sets)."""

from wredis._validation import validate_key, validate_score
from wredis._exceptions import ValidationError


class SortedSetManager:
    """Gestor simulado de conjuntos ordenados con validación."""

    def __init__(self):
        self._sets = {}

    def zadd(self, key: str, members: dict) -> int:
        """Agrega miembros con scores a un sorted set.

        Args:
            key: Nombre del sorted set.
            members: Diccionario {miembro: score}.

        Returns:
            Número de miembros agregados.
        """
        validate_key(key)

        # Validar todos los scores antes de agregar
        for member, score in members.items():
            validate_score(score)

        if key not in self._sets:
            self._sets[key] = {}

        self._sets[key].update(members)
        print(f"  ZADD {key}: {len(members)} miembros agregados")
        return len(members)

    def zrange(self, key: str):
        """Obtiene los miembros ordenados por score."""
        validate_key(key)
        if key not in self._sets:
            return []
        return sorted(self._sets[key].items(), key=lambda x: x[1])


# Crear gestor
manager = SortedSetManager()

print("=== Leaderboard válido ===")
leaderboard = {
    "jugador_alice": 1500.5,
    "jugador_bob": 2300,
    "jugador_carol": -100,
    "jugador_dave": 0,
    "jugador_eve": 9999.99,
}
manager.zadd("game:leaderboard", leaderboard)

print("\n=== Rankings ordenados ===")
ranking = manager.zrange("game:leaderboard")
for i, (member, score) in enumerate(ranking, 1):
    print(f"  #{i}: {member} = {score}")

print("\n=== Intentando agregar scores inválidos ===")

try:
    manager.zadd("game:leaderboard", {"jugador_fake": float("nan")})
except ValidationError as e:
    print(f"  Score NaN: {e}")

try:
    manager.zadd("game:leaderboard", {"jugador_fake": float("inf")})
except ValidationError as e:
    print(f"  Score inf: {e}")

try:
    manager.zadd("game:leaderboard", {"jugador_fake": "no_es_numero"})
except ValidationError as e:
    print(f"  Score string: {e}")

print("\nSe demostró la validación de scores en un gestor de sorted sets.")
