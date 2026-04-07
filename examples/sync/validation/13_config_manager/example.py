"""Validation integrated with a simulated configuration manager."""

from wredis._exceptions import ValidationError
from wredis._validation import validate_key, validate_ttl


class ConfigManager:
    """Configuration manager that uses wredis validation."""

    def __init__(self):
        self._store = {}

    def set_config(self, key: str, value, ttl: int = -1) -> bool:
        """Stores a configuration with prior validation."""
        # Validate parameters before storing
        validate_key(key)
        validate_ttl(ttl)

        self._store[key] = {"value": value, "ttl": ttl}
        print(f"  Configuration saved: {key} = {value}")
        return True

    def get_config(self, key: str):
        """Gets a configuration validating the key."""
        validate_key(key)
        return self._store.get(key)

    def list_configs(self):
        """Lists all stored configurations."""
        return dict(self._store)


# Create manager instance
manager = ConfigManager()

print("=== Saving valid configurations ===")
manager.set_config("app:name", "MyApplication")
manager.set_config("app:version", "2.0.0", ttl=86400)
manager.set_config("db:host", "localhost", ttl=-1)

print("\n=== Trying to save invalid configurations ===")

try:
    manager.set_config("", "invalid_value")
except ValidationError as e:
    print(f"  Error: {e}")

try:
    manager.set_config("app:debug", "true", ttl=-10)
except ValidationError as e:
    print(f"  Error: {e}")

print("\n=== Stored configurations ===")
for key, data in manager.list_configs().items():
    print(f"  {key}: {data['value']} (TTL: {data['ttl']})")

print("\nDemonstrated validation integration with a configuration manager.")
