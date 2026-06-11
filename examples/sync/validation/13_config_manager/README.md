# 13 Config Manager

## Description

Demonstrates integrating validation into a configuration manager class that validates keys and TTL before storing or retrieving configurations.

```mermaid
graph LR
    A[Config] --> B[ConfigManager]
    B --> C[Validator]
    C --> D[Store]
    C -->|Invalid| E[ValidationError]
```

## Code

See `example.py`

## Run

```bash
python example.py
```
