# 02 Custom Exceptions

## Description

Demonstrates configuring the @retry decorator to handle custom exception types beyond the default Redis exceptions.

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
