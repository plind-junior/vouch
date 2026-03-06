"""Append-only audit log at .vouch/audit.log.jsonl.

Every mutation goes through `log_event()`. Read with `read_events()` or
the `vouch audit` CLI command. The file is plain JSONL so it diffs and
greps cleanly in git history.
"""

from __future__ import annotations

import json
import os
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from .models import AuditEvent

AUDIT_FILENAME = "audit.log.jsonl"


def _audit_path(kb_dir: Path) -> Path:
    return kb_dir / AUDIT_FILENAME


def new_event_id() -> str:
    return uuid.uuid4().hex


def log_event(
    kb_dir: Path,
    *,
    event: str,
    actor: str,
    object_ids: list[str] | None = None,
    dry_run: bool = False,
    reversible: bool = True,
    data: dict[str, Any] | None = None,
) -> AuditEvent:
    """Append one AuditEvent. Returns the persisted event."""
    ev = AuditEvent(
        id=new_event_id(),
        event=event,
        actor=actor,
        object_ids=object_ids or [],
        dry_run=dry_run,
        reversible=reversible,
        data=data or {},
    )
    path = _audit_path(kb_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(ev.model_dump(mode="json"), separators=(",", ":"), sort_keys=True)
    # Open-write-close for crash safety — if the process dies mid-append the
    # log is still parseable up to the last newline.
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())
    return ev


def read_events(kb_dir: Path) -> Iterator[AuditEvent]:
    """Stream every event in order. Safely skips malformed lines."""
    path = _audit_path(kb_dir)
    if not path.exists():
        return
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield AuditEvent.model_validate(json.loads(line))
            except (json.JSONDecodeError, ValueError):
                continue


def count_events(kb_dir: Path) -> int:
    path = _audit_path(kb_dir)
    if not path.exists():
        return 0
    with path.open(encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())
