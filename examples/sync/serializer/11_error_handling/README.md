# 11 Error Handling

## Description

Demonstrates handling of SerializationError when attempting to serialize incompatible objects like sets, functions, custom objects, and invalid JSON.

```mermaid
graph LR
    A[Data] --> B[Serializer]
    B --> C{Redis}
    C -->|Error| D[Exception Handler]
```

## Code

See `example.py`

## Run

```bash
python example.py
```
