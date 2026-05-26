# 04 Redis Read Operations

## Description

Demonstrates using @retry decorator for Redis GET operations that may fail due to temporary connection issues.

```mermaid
graph LR
    A[Operation] --> B[Manager]
    B --> C{Redis}
    C -->|Success| D[Result]
    C -->|Error| E[Retry Handler]
```

## Code

See `example.py`

## Run

```bash
python example.py
```