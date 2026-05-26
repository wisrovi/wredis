# 11 Retry on Specific Errors

## Description

Demonstrates automatic retry mechanism with a decorator that only retries specific exception types (RedisConnectionError, OperationError) while immediately propagating others like ValidationError.

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