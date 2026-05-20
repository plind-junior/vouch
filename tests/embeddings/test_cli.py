"""CLI flag surface for embeddings commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from vouch.cli import cli
from vouch.embeddings import register
from vouch.embeddings.base import DEFAULT_MODEL_NAME
from vouch.models import Claim
from vouch.storage import KBStore
from tests.embeddings._fakes import MockEmbedder


@pytest.fixture(autouse=True)
def _register_default() -> None:
    register(DEFAULT_MODEL_NAME, lambda: MockEmbedder(dim=8))


@pytest.fixture
def kb(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    store = KBStore.init(tmp_path)
    src = store.put_source(b"e")
    store.put_claim(Claim(id="c1", text="some text", evidence=[src.id]))
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_search_semantic_flag(kb: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "some text", "--semantic"])
    assert result.exit_code == 0
    assert "c1" in result.output


def test_search_backend_flag(kb: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "some text", "--backend", "embedding"])
    assert result.exit_code == 0


def test_search_top_k_flag(kb: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "x", "--top-k", "3"])
    assert result.exit_code == 0
