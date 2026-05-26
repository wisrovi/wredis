# 09 Serialization Error Handling

## Description

Demonstrates handling of SerializationError including serialization failures, corrupted JSON, and fallback strategies.

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