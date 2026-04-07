# 06 Database Connection

## Description

Demonstrates using @retry decorator for establishing resilient Redis connections that can recover from temporary network failures.

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