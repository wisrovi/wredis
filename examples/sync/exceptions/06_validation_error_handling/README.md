# 06 Validation Error Handling

## Description

Demonstrates how to use ValidationError for input validation before sending data to Redis, showing various validation scenarios.

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
