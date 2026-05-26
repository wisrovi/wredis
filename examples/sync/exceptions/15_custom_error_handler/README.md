# 15 Custom Error Handler

## Description

Demonstrates creating centralized and reusable error handlers for WRedis exceptions, including a handler class with registered callbacks and a decorator pattern for automatic error handling.

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