"""Input validation for WRedis."""

from __future__ import annotations

from wredis._exceptions import ValidationError


def validate_ttl(ttl: int) -> None:
    """Validate TTL value.

    Args:
        ttl: Time-to-live in seconds. -1 means no TTL.

    Raises:
        ValidationError: If TTL is 0 or less than -1.
    """
    if ttl < -1:
        raise ValidationError(f"TTL must be -1 (no expiry) or positive, got {ttl}")


def validate_key(key: str) -> None:
    """Validate Redis key.

    Args:
        key: Redis key to validate.

    Raises:
        ValidationError: If key is empty or too long.
    """
    if not key:
        raise ValidationError("Redis key cannot be empty")
    if len(key) > 512:
        raise ValidationError(f"Redis key too long (max 512 bytes), got {len(key)}")


def validate_offset(offset: int) -> None:
    """Validate bitmap offset.

    Args:
        offset: Bit offset.

    Raises:
        ValidationError: If offset is negative.
    """
    if offset < 0:
        raise ValidationError(f"Bitmap offset must be non-negative, got {offset}")


def validate_bit_value(value: int) -> None:
    """Validate bit value.

    Args:
        value: Bit value (0 or 1).

    Raises:
        ValidationError: If value is not 0 or 1.
    """
    if value not in (0, 1):
        raise ValidationError(f"Bit value must be 0 or 1, got {value}")


def validate_score(score: float) -> None:
    """Validate sorted set score.

    Args:
        score: Score value.

    Raises:
        ValidationError: If score is not a valid number.
    """
    import math

    if not isinstance(score, (int, float)):
        raise ValidationError(f"Score must be a number, got {type(score).__name__}")
    if math.isnan(score) or math.isinf(score):
        raise ValidationError("Score cannot be NaN or infinity")
