# WRedis Makefile
# Targets for development, testing, and documentation

.PHONY: help install test test-cov lint format docs docs-clean docs-serve clean

# Default target
help:
	@echo "WRedis Makefile targets:"
	@echo ""
	@echo "  install       Install package with dev dependencies"
	@echo "  test          Run unit and integration tests"
	@echo "  test-cov      Run tests with coverage report"
	@echo "  lint          Run ruff linter"
	@echo "  format        Run ruff formatter"
	@echo "  docs          Build Sphinx documentation"
	@echo "  docs-clean    Clean documentation build artifacts"
	@echo "  docs-serve    Build docs and start local server"
	@echo "  clean         Remove all build artifacts"

# Install dependencies
install:
	pip install -e ".[dev,docs]"

# Run tests
test:
	python -m pytest tests/ -v

# Run tests with coverage
test-cov:
	python -m pytest tests/ --cov=wredis --cov-report=term-missing --cov-report=html

# Lint code
lint:
	python -m ruff check wredis/ tests/

# Format code
format:
	python -m ruff format wredis/ tests/
	python -m ruff check wredis/ tests/ --fix

# Build Sphinx documentation
docs:
	cd docs && sphinx-build -b html . _build/html

# Clean documentation build artifacts
docs-clean:
	rm -rf docs/_build

# Build docs and start local server
docs-serve: docs
	@echo "Documentation available at http://localhost:8000"
	@echo "Press Ctrl+C to stop the server"
	cd docs/_build/html && python -m http.server 8000

# Clean all build artifacts
clean: docs-clean
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.json
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
