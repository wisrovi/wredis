"""Example demonstrating Forensic Ghost Audit Logging in wredis."""

import json
import fakeredis
from wredis.hash import RedisHashManager
from wredis.forensic import FORENSIC_STREAM_NAME

def main():
    print("=== WRedis Forensic Audit Log Example ===")
    
    # Use fake Redis client for standalone execution
    client = fakeredis.FakeRedis(decode_responses=True)
    
    # Create RedisHashManager with forensic audit logging ENABLED
    manager = RedisHashManager(verbose=True, forensic=True)
    manager.redis_client = client

    # Perform a operation
    print("\n1. Writing hash with forensic mode ON...")
    manager.create_hash("user_profile", "user:101", {"name": "Bob", "role": "admin"})

    # Inspect audit log stream
    print(f"\n2. Inspecting audit stream '{FORENSIC_STREAM_NAME}'...")
    entries = client.xrange(FORENSIC_STREAM_NAME)
    for msg_id, data in entries:
        print(f"Audit Event ID: {msg_id}")
        print(f"  Target Key: {data['table_name']}")
        print(f"  Action:     {data['action']}")
        print(f"  After State:{data['after']}")

if __name__ == "__main__":
    main()
