"""Model-identity migration and backfill."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .. import index_db
from .base import get_embedder


def detect_mismatch(kb_dir: Path) -> dict[str, Any] | None:
    """Return mismatch info or None if no mismatch."""
    meta = index_db.get_embedding_meta(kb_dir)
    stored = meta.get("embedding_model")
    if not stored:
        return None
    try:
        current = get_embedder()
    except KeyError:
        return None
    if current.name == stored:
        return None
    return {
        "stored_model": stored,
        "stored_version": meta.get("embedding_model_version"),
        "stored_dim": meta.get("embedding_dim"),
        "current_model": current.name,
        "current_version": current.version,
        "current_dim": current.dim,
    }


def backfill_embeddings(store: Any, *, force: bool = False) -> int:
    """Re-encode every artifact under the current adapter. Returns count touched."""
    embedder = get_embedder()
    touched = 0
    try:
        for c in store.list_claims():
            store._embed_and_store(kind="claim", id=c.id, text=c.text)
            touched += 1
    except AttributeError:
        pass
    try:
        for p in store.list_pages():
            store._embed_and_store(kind="page", id=p.id, text=f"{p.title}\n\n{p.body}")
            touched += 1
    except AttributeError:
        pass
    try:
        for s in store.list_sources():
            store._embed_and_store(
                kind="source", id=s.id, text=s.title or s.locator or "",
            )
            touched += 1
    except AttributeError:
        pass
    try:
        for e in store.list_entities():
            store._embed_and_store(
                kind="entity", id=e.id, text=f"{e.name}\n\n{e.description or ''}",
            )
            touched += 1
    except AttributeError:
        pass
    try:
        for r in store.list_relations():
            store._embed_and_store(
                kind="relation", id=r.id,
                text=f"{r.source} {r.relation.value} {r.target}",
            )
            touched += 1
    except AttributeError:
        pass
    try:
        for ev in store.list_evidence():
            store._embed_and_store(kind="evidence", id=ev.id, text=ev.quote or "")
            touched += 1
    except AttributeError:
        pass
    index_db.set_embedding_meta(
        store.kb_dir, model=embedder.name, version=embedder.version, dim=embedder.dim,
    )
    return touched
