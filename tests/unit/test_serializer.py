"""Tests for serializer module."""

import pytest

from wredis._exceptions import SerializationError
from wredis._serializer import deserialize, serialize


class TestSerializer:
    """Tests for serialize and deserialize functions."""

    def test_serialize_dict(self):
        """Test serializing a dictionary."""
        result = serialize({"key": "value", "num": 42})
        assert result == '{"key": "value", "num": 42}'

    def test_serialize_list(self):
        """Test serializing a list."""
        result = serialize([1, 2, 3])
        assert result == "[1, 2, 3]"

    def test_serialize_string(self):
        """Test serializing a string."""
        result = serialize("hello")
        assert result == '"hello"'

    def test_serialize_number(self):
        """Test serializing a number."""
        assert serialize(42) == "42"
        assert serialize(3.14) == "3.14"

    def test_serialize_none(self):
        """Test serializing None."""
        assert serialize(None) == "null"

    def test_serialize_unicode(self):
        """Test serializing unicode characters."""
        result = serialize({"name": "café"})
        assert "café" in result

    def test_serialize_unserializable(self):
        """Test serializing unserializable object raises error."""
        with pytest.raises(SerializationError):
            serialize(object())

    def test_deserialize_dict(self):
        """Test deserializing a dictionary."""
        result = deserialize('{"key": "value"}')
        assert result == {"key": "value"}

    def test_deserialize_list(self):
        """Test deserializing a list."""
        result = deserialize("[1, 2, 3]")
        assert result == [1, 2, 3]

    def test_deserialize_string(self):
        """Test deserializing a string."""
        result = deserialize('"hello"')
        assert result == "hello"

    def test_deserialize_number(self):
        """Test deserializing a number."""
        assert deserialize("42") == 42

    def test_deserialize_none(self):
        """Test deserializing null."""
        assert deserialize("null") is None

    def test_deserialize_invalid_json(self):
        """Test deserializing invalid JSON raises error."""
        with pytest.raises(SerializationError):
            deserialize("not json")

    def test_deserialize_invalid_type(self):
        """Test deserializing non-string raises error."""
        with pytest.raises(SerializationError):
            deserialize(123)
