"""Score validation for sorted set operations."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_key, validate_score


class SortedSetManager:
    """Simulated sorted set manager with validation."""

    def __init__(self):
        self._sets = {}

    def zadd(self, key: str, members: dict) -> int:
        """Adds members with scores to a sorted set.

        Args:
            key: Name of the sorted set.
            members: Dictionary {member: score}.

        Returns:
            Number of members added.
        """
        validate_key(key)

        # Validate all scores before adding
        for member, score in members.items():
            validate_score(score)

        if key not in self._sets:
            self._sets[key] = {}

        self._sets[key].update(members)
        print(f"  ZADD {key}: {len(members)} members added")
        return len(members)

    def zrange(self, key: str):
        """Gets members ordered by score."""
        validate_key(key)
        if key not in self._sets:
            return []
        return sorted(self._sets[key].items(), key=lambda x: x[1])


# Create manager
manager = SortedSetManager()

print("=== Valid leaderboard ===")
leaderboard = {
    "player_alice": 1500.5,
    "player_bob": 2300,
    "player_carol": -100,
    "player_dave": 0,
    "player_eve": 9999.99,
}
manager.zadd("game:leaderboard", leaderboard)

print("\n=== Ordered rankings ===")
ranking = manager.zrange("game:leaderboard")
for i, (member, score) in enumerate(ranking, 1):
    print(f"  #{i}: {member} = {score}")

print("\n=== Trying to add invalid scores ===")

try:
    manager.zadd("game:leaderboard", {"player_fake": float("nan")})
except ValidationError as e:
    print(f"  NaN score: {e}")

try:
    manager.zadd("game:leaderboard", {"player_fake": float("inf")})
except ValidationError as e:
    print(f"  Infinite score: {e}")

try:
    manager.zadd("game:leaderboard", {"player_fake": "not_a_number"})
except ValidationError as e:
    print(f"  String score: {e}")

print("\nDemonstrated score validation in a sorted set manager.")
