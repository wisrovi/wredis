#!/bin/bash
set -e

echo "=== Running coverage analysis for wredis ==="
PYTHONPATH=. pytest --cov=wredis --cov-report=term-missing tests/unit/
