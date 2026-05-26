"""JSON serializer for WRedis."""
from __future__ import annotations

import json
from typing import Any

from wredis._exceptions import SerializationError


def serialize(value: Any) -> str:
    """Serialize a value to JSON string.

    Args:
        value: Value to serialize.

    Returns:
        JSON string.

    Raises:
        SerializationError: If serialization fails.
    """
    try:
        return json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise SerializationError(f"Failed to serialize value: {e}") from e


def deserialize(data: str) -> Any:
    """Deserialize a JSON string to Python object.

    Args:
        data: JSON string to deserialize.

    Returns:
        Deserialized Python object.

    Raises:
        SerializationError: If deserialization fails.
    """
    try:
        return json.loads(data)
    except (TypeError, ValueError, json.JSONDecodeError) as e:
        raise SerializationError(f"Failed to deserialize data: {e}") from e
