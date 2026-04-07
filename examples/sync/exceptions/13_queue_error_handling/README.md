# 13 Queue Error Handling

## Description

Demonstrates handling of QueueError for queue operations including push, pop, peek, and scenarios like full queue, empty queue, and invalid elements.

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