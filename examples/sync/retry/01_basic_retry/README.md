# 01 Basic Retry

## Description

Demonstrates basic usage of the @retry decorator that automatically retries failed operations up to a specified number of attempts.

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
