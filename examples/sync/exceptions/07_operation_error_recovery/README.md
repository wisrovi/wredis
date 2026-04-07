# 07 Operation Error Recovery

## Description

Demonstrates recovery strategies for OperationError including retries and fallback to default values.

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