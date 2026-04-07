"""Serialization of dates and times using datetime.

This example demonstrates how to serialize datetime objects
by converting them to ISO 8601 strings, since json.dumps does
not natively support datetime. The default=str parameter is
used for automatic conversion.
"""

import json
from datetime import date, datetime, time, timedelta

from wredis._serializer import deserialize, serialize

# Convert datetime to ISO string before serializing
now = datetime.now()
date_str = now.isoformat()
serialized = serialize(date_str)
print(f"Original datetime: {now}")
print(f"Converted to ISO: {date_str}")
print(f"Serialized: {serialized}")
restored = deserialize(serialized)
print(f"Deserialized: {restored}")
print(f"Converted back to datetime: {datetime.fromisoformat(restored)}")
print()

# Date as string
today = date.today()
date_str = today.isoformat()
serialized = serialize(date_str)
print(f"Original date: {today}")
print(f"Converted to ISO: {date_str}")
print(f"Serialized: {serialized}")
print(f"Deserialized: {deserialize(serialized)}")
print()

# Dictionary with multiple date fields
record = {
    "event": "conference",
    "start_date": date(2024, 6, 15).isoformat(),
    "end_date": date(2024, 6, 17).isoformat(),
    "created_at": datetime(2024, 1, 1, 10, 30, 0).isoformat(),
}
serialized = serialize(record)
print(f"Record with dates: {record}")
print(f"Serialized: {serialized}")
restored = deserialize(serialized)
print(f"Deserialized: {restored}")
print(f"Start date as date: {date.fromisoformat(restored['start_date'])}")
