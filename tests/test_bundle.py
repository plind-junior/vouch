"""Portable bundle export / import round-trip."""

from __future__ import annotations

from pathlib import Path

import pytest

from vouch import bundle
from vouch.models import Claim, Page
from vouch.storage import KBStore


@pytest.fixture
def store(tmp_path: Path) -> KBStore:
    return KBStore.init(tmp_path)


def test_export_import_round_trip(store: KBStore, tmp_path: Path) -> None:
    src = store.put_source(b"e", title="doc")
    store.put_claim(Claim(id="c1", text="alpha", evidence=[src.id]))
    store.put_page(Page(id="p1", title="Page one"))
    bundle_path = tmp_path / "out.tar.gz"
    manifest = bundle.export(store.kb_dir, dest=bundle_path)
    assert bundle_path.exists()
    assert manifest["counts"]["claims"] == 1
    chk = bundle.export_check(bundle_path)
    assert chk.ok

    dest_root = tmp_path / "dest"
    dest = KBStore.init(dest_root)
    diff = bundle.import_check(dest.kb_dir, bundle_path)
    assert diff.ok
    assert diff.conflicts == []
    assert len(diff.new_files) >= 3
    result = bundle.import_apply(dest.kb_dir, bundle_path)
    assert result["bundle_id"] == manifest["bundle_id"]
    assert len(result["written"]) >= 3
    assert dest.get_claim("c1").text == "alpha"


def test_import_apply_skips_conflicts_by_default(store: KBStore, tmp_path: Path) -> None:
    src = store.put_source(b"e")
    store.put_claim(Claim(id="c1", text="first", evidence=[src.id]))
    bundle_path = tmp_path / "b.tar.gz"
    bundle.export(store.kb_dir, dest=bundle_path)
    c = store.get_claim("c1")
    c.text = "changed"
    store.update_claim(c)
    result = bundle.import_apply(store.kb_dir, bundle_path, on_conflict="skip")
    assert result["skipped_conflicts"]
    assert store.get_claim("c1").text == "changed"


def test_import_apply_fails_when_requested(store: KBStore, tmp_path: Path) -> None:
    src = store.put_source(b"e")
    store.put_claim(Claim(id="c1", text="first", evidence=[src.id]))
    bundle_path = tmp_path / "b.tar.gz"
    bundle.export(store.kb_dir, dest=bundle_path)
    c = store.get_claim("c1")
    c.text = "changed"
    store.update_claim(c)
    with pytest.raises(RuntimeError, match="conflicts"):
        bundle.import_apply(store.kb_dir, bundle_path, on_conflict="fail")


def test_import_check_rejects_invalid_claim_content(
    store: KBStore, tmp_path: Path,
) -> None:
    import io
    import json
    import tarfile
    from vouch.storage import sha256_hex

    bad_body = b"confidence: 999\ntext: null\n"
    manifest = {
        "spec": "vouch-bundle-0.1",
        "bundle_id": "abc",
        "files": [
            {
                "path": "claims/bad.yaml",
                "size": len(bad_body),
                "sha256": sha256_hex(bad_body),
            },
        ],
        "counts": {"claims": 1},
        "safety": {
            "has_proposed": False,
            "has_state_db": False,
            "has_audit_log": False,
        },
    }
    bundle_path = tmp_path / "evil.tar.gz"
    with tarfile.open(bundle_path, "w:gz") as tar:
        info = tarfile.TarInfo("claims/bad.yaml")
        info.size = len(bad_body)
        tar.addfile(info, io.BytesIO(bad_body))
        mf = json.dumps(manifest).encode()
        info = tarfile.TarInfo("manifest.json")
        info.size = len(mf)
        tar.addfile(info, io.BytesIO(mf))

    chk = bundle.import_check(store.kb_dir, bundle_path)
    assert not chk.ok
    assert any("schema validation failed" in i for i in chk.issues)


def test_import_apply_skips_invalid_content(
    store: KBStore, tmp_path: Path,
) -> None:
    import io
    import json
    import tarfile
    from vouch.storage import sha256_hex

    bad_body = b"confidence: 999\ntext: null\n"
    manifest = {
        "spec": "vouch-bundle-0.1",
        "bundle_id": "abc",
        "files": [
            {
                "path": "claims/bad.yaml",
                "size": len(bad_body),
                "sha256": sha256_hex(bad_body),
            },
        ],
        "counts": {"claims": 1},
        "safety": {
            "has_proposed": False,
            "has_state_db": False,
            "has_audit_log": False,
        },
    }
    bundle_path = tmp_path / "evil.tar.gz"
    with tarfile.open(bundle_path, "w:gz") as tar:
        info = tarfile.TarInfo("claims/bad.yaml")
        info.size = len(bad_body)
        tar.addfile(info, io.BytesIO(bad_body))
        mf = json.dumps(manifest).encode()
        info = tarfile.TarInfo("manifest.json")
        info.size = len(mf)
        tar.addfile(info, io.BytesIO(mf))

    result = bundle.import_apply(store.kb_dir, bundle_path)
    assert not any(Path(p).name == "bad.yaml" for p in result["written"])
