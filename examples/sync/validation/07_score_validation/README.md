# 07 Score Validation

## Description

Demonstrates score validation for sorted sets, showing valid scores (integers, floats, negative) and invalid scores (NaN, infinity).

```mermaid
graph LR
    A[Score] --> B[Validator]
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
