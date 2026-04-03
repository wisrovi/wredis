"""Tests for retry module."""

import time
from unittest.mock import MagicMock, patch

import pytest
import redis

from wredis._exceptions import OperationError
from wredis._retry import async_retry, retry


class TestRetry:
    """Tests for retry decorator."""

    def test_retry_success_first_attempt(self):
        """Test function succeeds on first attempt."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        def func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = func()
        assert result == "success"
        assert call_count == 1

    def test_retry_success_after_failures(self):
        """Test function succeeds after failures."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01, exceptions=(ConnectionError,))
        def func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("temp failure")
            return "success"

        result = func()
        assert result == "success"
        assert call_count == 3

    def test_retry_all_attempts_fail(self):
        """Test all attempts fail raises OperationError."""

        @retry(max_attempts=2, delay=0.01, exceptions=(ConnectionError,))
        def func():
            raise ConnectionError("permanent failure")

        with pytest.raises(OperationError):
            func()

    def test_retry_custom_exceptions(self):
        """Test retry only on specified exceptions."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def func():
            nonlocal call_count
            call_count += 1
            raise TypeError("not retried")

        with pytest.raises(TypeError):
            func()
        assert call_count == 1

    def test_retry_backoff(self):
        """Test exponential backoff increases delay."""
        delays = []

        @retry(max_attempts=3, delay=0.01, backoff=2.0, exceptions=(ConnectionError,))
        def func():
            raise ConnectionError("fail")

        def mock_sleep(delay):
            delays.append(delay)

        with patch("time.sleep", mock_sleep), pytest.raises(OperationError):
            func()

        assert len(delays) == 2
        assert delays[1] > delays[0]


class TestAsyncRetry:
    """Tests for async_retry decorator."""

    @pytest.mark.asyncio
    async def test_async_retry_success_first_attempt(self):
        """Test async function succeeds on first attempt."""
        call_count = 0

        @async_retry(max_attempts=3, delay=0.01)
        async def func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await func()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_async_retry_success_after_failures(self):
        """Test async function succeeds after failures."""
        call_count = 0

        @async_retry(max_attempts=3, delay=0.01, exceptions=(ConnectionError,))
        async def func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("temp failure")
            return "success"

        result = await func()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_async_retry_all_attempts_fail(self):
        """Test all async attempts fail raises OperationError."""

        @async_retry(max_attempts=2, delay=0.01, exceptions=(ConnectionError,))
        async def func():
            raise ConnectionError("permanent failure")

        with pytest.raises(OperationError):
            await func()
