# 12 Retry with Fallback

## Description

Demonstrates a pattern where if Redis fails after all retries, a local in-memory cache is used as fallback.

```mermaid
graph LR
    A[Operation] --> B[Manager]
    B --> C{Redis}
    C -->|Success| D[Result]
    C -->|Error| E[Fallback Handler]
```

## Code

See `example.py`

## Run

```bash
python example.py
```