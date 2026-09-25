#!/bin/bash
set -e

echo "=== Running unit tests for wredis inside Docker ==="

docker run --rm \
  -v "$(pwd):/app" \
  -w /app \
  python:3.11-slim \
  bash -c "pip install --no-cache-dir . pytest pytest-asyncio fakeredis loguru && PYTHONPATH=. pytest tests/unit/"

echo "=== Docker tests completed successfully ==="
