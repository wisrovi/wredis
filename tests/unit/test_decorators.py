"""Unit tests for wredis.decorators - simple coverage."""

from unittest.mock import MagicMock, patch

import pytest

import wredis.decorators


class TestDecorators:
    """Tests for wredis decorators."""

    @patch("wredis.decorators.redis.Redis")
    def test_cache_decorator(self, mock_redis):
        """Test cache decorator."""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.get.return_value = None
        mock_client.set.return_value = True

        @wredis.decorators.cache(ttl=60)
        def test_func(x):
            return x * 2

        result = test_func(5)
        assert result == 10

    @patch("wredis.decorators.redis.Redis")
    def test_cache_with_args(self, mock_redis):
        """Test cache with arguments."""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.get.return_value = None

        @wredis.decorators.cache(ttl=60, prefix="test_prefix")
        def test_func(x, y):
            return x + y

        result = test_func(1, 2)
        assert result == 3


class TestDecoratorsImport:
    """Test that decorators can be imported."""

    def test_import_cache(self):
        """Test importing cache."""
        from wredis.decorators import cache

        assert callable(cache)

    def test_import_async_cache(self):
        """Test importing async_cache."""
        from wredis.decorators import async_cache

        assert callable(async_cache)

    def test_import_invalidate_cache(self):
        """Test importing invalidate_cache."""
        from wredis.decorators import invalidate_cache

        assert callable(invalidate_cache)
