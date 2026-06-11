# 02 Invalid TTL

## Description

Demonstrates that TTL values less than -1 raise ValidationError, as these are invalid TTL values.

```mermaid
graph LR
    A[TTL Value] --> B[Validator]
    B --> C{Valid?}
    C -->|Yes| D[Accept]
    C -->|No| E[ValidationError]
```

## Code

See `example.py`

## Run

```bash
python example.py
```
