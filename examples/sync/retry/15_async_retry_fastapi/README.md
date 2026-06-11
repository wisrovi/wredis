# 15 Async Retry FastAPI

## Description

Demonstrates integrating async_retry with FastAPI endpoints to create resilient APIs that can handle Redis failures gracefully.

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
