"""SQLite FTS5 index — rebuild, search, special characters."""

from __future__ import annotations

from pathlib import Path

import pytest

from vouch import health, index_db
from vouch.models import Claim, Entity, EntityType, Page
from vouch.proposals import approve, propose_claim
from vouch.storage import KBStore


@pytest.fixture
def store(tmp_path: Path) -> KBStore:
    return KBStore.init(tmp_path)


def test_index_rebuild_then_search(store: KBStore) -> None:
    src = store.put_source(b"e")
    store.put_claim(Claim(id="c1", text="JWT tokens are stateless",
                          evidence=[src.id]))
    store.put_page(Page(id="p1", title="Auth", body="overview of auth"))
    store.put_entity(Entity(id="e1", name="JWT", type=EntityType.CONCEPT))
    health.rebuild_index(store)
    hits = index_db.search(store.kb_dir, "JWT")
    kinds = {k for k, *_ in hits}
    assert "claim" in kinds
    assert "entity" in kinds


def test_search_handles_special_chars(store: KBStore) -> None:
    src = store.put_source(b"e")
    store.put_claim(Claim(id="c1", text="quote \"this\" and (parens)",
                          evidence=[src.id]))
    health.rebuild_index(store)
    # Should not crash on the FTS5-special characters.
    hits = index_db.search(store.kb_dir, 'quote "this"')
    assert any(k == "claim" for k, *_ in hits)


def test_index_via_approve(store: KBStore) -> None:
    src = store.put_source(b"e")
    pr = propose_claim(store, text="indexed automatically",
                       evidence=[src.id], proposed_by="a")
    approve(store, pr.id, approved_by="u")
    hits = index_db.search(store.kb_dir, "indexed")
    assert any(k == "claim" for k, *_ in hits)
