"""Enterprise Forensic Audit Log for wredis.

Records mutation events (INSERT, UPDATE, DELETE) into a Redis stream or hash audit log key
when forensic mode is enabled.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


FORENSIC_STREAM_NAME = "_forensic_audit_log"


def record_forensic_entry(
    redis_client: Any,
    table_name: str,
    action: str,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    stream_name: str = FORENSIC_STREAM_NAME,
) -> str | None:
    """Records a forensic audit log entry into Redis stream.

    Args:
        redis_client: Active Redis or FakeRedis client.
        table_name: Target key/hash/stream name.
        action: Operation type ('INSERT', 'UPDATE', 'DELETE').
        before: Pre-change state dict or None.
        after: Post-change state dict or None.
        stream_name: Name of the audit stream. Defaults to '_forensic_audit_log'.

    Returns:
        Generated stream message ID or None on failure.
    """
    try:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "table_name": table_name,
            "action": action.upper(),
            "before": json.dumps(before) if before is not None else None,
            "after": json.dumps(after) if after is not None else None,
        }
        # Clean null fields for Redis stream compatibility if needed
        payload = {k: (v if v is not None else "") for k, v in entry.items()}
        return redis_client.xadd(stream_name, payload)
    except Exception:
        return None
