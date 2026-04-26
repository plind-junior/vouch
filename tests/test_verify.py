"""Source verification — drift detection."""

from __future__ import annotations

from pathlib import Path

import pytest

from vouch import verify
from vouch.storage import KBStore


@pytest.fixture
def store(tmp_path: Path) -> KBStore:
    return KBStore.init(tmp_path)


def test_verify_detects_external_drift(store: KBStore, tmp_path: Path) -> None:
    f = tmp_path / "doc.txt"
    f.write_bytes(b"original")
    src = store.put_source(
        f.read_bytes(), title="doc",
        locator=str(f.resolve()),
    )
    # Now overwrite the external file.
    f.write_bytes(b"changed")
    results = verify.verify_all(store)
    target = next(r for r in results if r.source.id == src.id)
    assert target.stored_ok  # stored copy is still fine
    assert target.external_status == "drift"
