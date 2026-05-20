"""Test doubles for the embeddings layer.

MockEmbedder returns deterministic float32 vectors derived from sha256
of the input. No network, no model, runs in microseconds.
"""

from __future__ import annotations

import hashlib
import struct
from collections.abc import Sequence

import numpy as np

from vouch.embeddings.base import Embedder


class MockEmbedder(Embedder):
    """Deterministic embedder for tests."""

    name = "mock"
    version = "1"

    def __init__(self, dim: int = 8) -> None:
        self.dim = dim

    def encode(self, text: str) -> np.ndarray:
        out = np.zeros(self.dim, dtype=np.float32)
        i = 0
        seed = text.encode("utf-8")
        while i < self.dim:
            h = hashlib.sha256(seed).digest()
            for j in range(0, len(h) - 3, 4):
                if i >= self.dim:
                    break
                out[i] = struct.unpack("<f", h[j:j + 4])[0]
                i += 1
            seed = h
        norm = float(np.linalg.norm(out))
        if norm > 0:
            out /= norm
        return out

    def encode_batch(self, texts: Sequence[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        return np.stack([self.encode(t) for t in texts])
