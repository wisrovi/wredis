# Sets Read Example

## Description

This example demonstrates reading members from a Redis set using `RedisSetManager`.

## Diagram

```mermaid
flowchart TD
    A[Start] --> B[Create Set manager]
    B --> C[Get all set members]
    C --> D[Display results]
    D --> E[End]
```

## Code

```python
from wredis.sets import RedisSetManager

set_manager = RedisSetManager(host="localhost")


print(set_manager.get_set_members("my_set"))
```

## Run Instructions

```bash
python example.py
```
