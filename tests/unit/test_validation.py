"""Tests for validation module."""

import pytest

from wredis._exceptions import ValidationError
from wredis._validation import (
    validate_bit_value,
    validate_key,
    validate_offset,
    validate_score,
    validate_ttl,
)


class TestValidation:
    """Tests for validation functions."""

    def test_validate_ttl_valid(self):
        """Test valid TTL values."""
        validate_ttl(-1)
        validate_ttl(0)
        validate_ttl(60)
        validate_ttl(3600)

    def test_validate_ttl_invalid(self):
        """Test invalid TTL values."""
        with pytest.raises(ValidationError):
            validate_ttl(-2)

    def test_validate_key_valid(self):
        """Test valid keys."""
        validate_key("mykey")
        validate_key("user:1001:profile")
        validate_key("a" * 512)

    def test_validate_key_empty(self):
        """Test empty key raises error."""
        with pytest.raises(ValidationError):
            validate_key("")

    def test_validate_key_too_long(self):
        """Test key too long raises error."""
        with pytest.raises(ValidationError):
            validate_key("a" * 513)

    def test_validate_offset_valid(self):
        """Test valid offsets."""
        validate_offset(0)
        validate_offset(100)
        validate_offset(999999)

    def test_validate_offset_negative(self):
        """Test negative offset raises error."""
        with pytest.raises(ValidationError):
            validate_offset(-1)

    def test_validate_bit_value_valid(self):
        """Test valid bit values."""
        validate_bit_value(0)
        validate_bit_value(1)

    def test_validate_bit_value_invalid(self):
        """Test invalid bit values raise error."""
        with pytest.raises(ValidationError):
            validate_bit_value(2)
        with pytest.raises(ValidationError):
            validate_bit_value(-1)

    def test_validate_score_valid(self):
        """Test valid scores."""
        validate_score(0)
        validate_score(1.5)
        validate_score(-100)

    def test_validate_score_nan(self):
        """Test NaN score raises error."""
        import math

        with pytest.raises(ValidationError):
            validate_score(float("nan"))

    def test_validate_score_inf(self):
        """Test infinity score raises error."""
        with pytest.raises(ValidationError):
            validate_score(float("inf"))

    def test_validate_score_string(self):
        """Test string score raises error."""
        with pytest.raises(ValidationError):
            validate_score("not_a_number")
