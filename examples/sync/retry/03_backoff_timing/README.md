# 03 Backoff Timing

## Description

Demonstrates exponential backoff timing where the delay between retries increases exponentially with each attempt.

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
