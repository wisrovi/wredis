# 05 Redis Write Operations

## Description

Demonstrates using @retry decorator for Redis SET/HSET write operations that may fail and need safe retry mechanisms.

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
