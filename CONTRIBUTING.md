# Contributing to WRedis

Welcome! We're excited that you're interested in contributing to WRedis.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to wisrovi.rodriguez@gmail.com.

## Getting Started

- Fork the repository
- Clone your fork: `git clone https://github.com/YOUR_USERNAME/wredis.git`
- Add upstream: `git remote add upstream https://github.com/wisrovi/wredis.git`

## Development Environment

### Prerequisites

- Python 3.10+
- Docker (for running Redis during tests)

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

### Running Redis

```bash
# Using Docker Compose
cd environment
docker-compose up -d

# Or using Makefile
make start
```

## Making Changes

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Add tests if applicable
4. Ensure code quality checks pass

## Testing

### Run all tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=wredis --cov-fail-under=95 --cov-report=term-missing
```

### Run specific test file

```bash
pytest tests/test_bitmap.py
```

### Run with Redis (integration tests)

```bash
# Ensure Redis is running
docker-compose -f environment/docker-compose.yml up -d

# Run tests
pytest --integration
```

## Code Quality

### Ruff (Linting & Formatting)

```bash
# Check for errors
ruff check .

# Fix auto-fixable errors
ruff check . --fix

# Format code
ruff format .
```

### MyPy (Type Checking)

```bash
mypy src/wredis
```

### Pre-commit hooks

```bash
# Run all pre-commit hooks
pre-commit run --all-files
```

## Submitting Changes

### Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Ensure code quality checks pass (ruff, mypy, coverage)
5. Update CHANGELOG.md with your changes under the `[Unreleased]` section
6. Submit a Pull Request

### PR Title Format

Use conventional commits format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `chore:` Maintenance

Example: `feat: Add async_cache decorator`

### PR Description

Include:
- Summary of changes
- Related issue number (if applicable)
- Testing performed

## Directory Structure

```
wredis/
├── src/wredis/           # Main package
│   ├── bitmap/          # Bitmap operations
│   ├── hash/            # Hash operations
│   ├── pubsub/          # Pub/Sub
│   ├── queue/           # Queue operations
│   ├── sets/            # Set operations
│   ├── sortedset/       # Sorted set operations
│   ├── streams/         # Stream operations
│   ├── async_api/       # Async versions of all managers
│   ├── ha/              # High availability (Sentinel/Cluster)
│   ├── decorators.py    # @cache, @async_cache decorators
│   ├── _types.py        # Type aliases
│   ├── _exceptions.py   # Custom exceptions
│   └── _connection.py   # Connection factories
├── tests/               # Test suite
├── examples/            # Example scripts
├── environment/          # Docker Compose files
└── site/                # Marketing website
```

## Common Issues

### Redis Connection Errors

If you get connection errors, ensure Redis is running:

```bash
docker ps | grep redis
# If not running:
docker-compose -f environment/docker-compose.yml up -d
```

### Import Errors

If you get import errors after making changes:

```bash
pip install -e . --force-reinstall
```

## Contact

- Email: wisrovi.rodriguez@gmail.com
- GitHub Issues: https://github.com/wisrovi/wredis/issues
