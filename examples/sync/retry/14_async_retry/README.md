# 14 Async Retry

## Description

Demonstrates using async_retry decorator for async/await functions with automatic retry using asyncio.sleep.

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
