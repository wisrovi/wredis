"""Unit tests for wredis forensic audit logging."""

import json
import pytest
import fakeredis
from wredis.hash import RedisHashManager
from wredis.forensic import record_forensic_entry, FORENSIC_STREAM_NAME


def test_record_forensic_entry():
    client = fakeredis.FakeRedis(decode_responses=True)
    msg_id = record_forensic_entry(
        client,
        table_name="users",
        action="INSERT",
        before=None,
        after={"name": "Alice", "age": 30}
    )
    assert msg_id is not None
    entries = client.xrange(FORENSIC_STREAM_NAME)
    assert len(entries) == 1
    _, data = entries[0]
    assert data["table_name"] == "users"
    assert data["action"] == "INSERT"
    assert json.loads(data["after"]) == {"name": "Alice", "age": 30}


def test_redis_hash_manager_forensic_enabled():
    client = fakeredis.FakeRedis(decode_responses=True)
    mgr = RedisHashManager(verbose=False, forensic=True)
    mgr.redis_client = client

    mgr.create_hash("user_session", "session1", {"user_id": 123})
    entries = client.xrange(FORENSIC_STREAM_NAME)
    assert len(entries) == 1
    _, data = entries[0]
    assert data["table_name"] == "user_session"
    assert data["action"] == "INSERT"
