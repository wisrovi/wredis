# 12 Graceful Degradation

## Description

Demonstrates graceful degradation pattern where the application continues to function with reduced capabilities (using in-memory fallback) when Redis is unavailable.

```mermaid
graph LR
    A[Operation] --> B[Manager]
    B --> C{Redis}
    C -->|Success| D[Result]
    C -->|Error| E[Exception Handler]
```

## Code

See `example.py`

## Run

```bash
python example.py
```