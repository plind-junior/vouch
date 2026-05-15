"""Synthesize a vouch KB of N claims for benchmarking.

Deterministic for a given seed. Generates plausible-shaped data, not
real data — claim text is templated, sources are synthetic.

Usage:
    python benchmarks/fixtures/gen_kb.py --out /tmp/bench-kb --claims 10000

Not part of the public API. Lives under benchmarks/ on purpose.
"""

from __future__ import annotations

import argparse
import hashlib
import random
import sys
from pathlib import Path


SUBJECTS = [
    "auth", "session", "cache", "queue", "scheduler", "billing",
    "search", "index", "rate-limit", "webhook", "audit", "feature-flag",
]
VERBS = [
    "uses", "requires", "rejects", "logs", "retries", "ignores",
    "caches", "validates", "rate-limits", "fans-out", "back-fills",
]
OBJECTS = [
    "JWT", "Redis", "Postgres", "SQS", "TLS 1.3", "OIDC",
    "exponential backoff", "idempotency keys", "rolling window",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output directory for .vouch/")
    ap.add_argument("--claims", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    root = Path(args.out) / ".vouch"
    (root / "claims").mkdir(parents=True, exist_ok=True)
    (root / "sources").mkdir(parents=True, exist_ok=True)

    # Pool of sources to cite from
    source_ids = []
    for i in range(max(50, args.claims // 20)):
        body = f"synthetic source {i}: {rng.choice(SUBJECTS)} notes"
        digest = hashlib.sha256(body.encode()).hexdigest()
        sd = root / "sources" / digest
        sd.mkdir(exist_ok=True)
        (sd / "content").write_text(body)
        (sd / "meta.yaml").write_text(
            f"id: {digest}\ntype: file\nlocator: synthetic-{i}\n"
            f"title: synthetic source {i}\nbyte_size: {len(body)}\n"
        )
        source_ids.append(digest)

    for i in range(args.claims):
        s, v, o = rng.choice(SUBJECTS), rng.choice(VERBS), rng.choice(OBJECTS)
        cid = f"{s}-{v.replace(' ', '-')}-{o.lower().replace(' ', '-')}-{i:06d}"
        text = f"{s} {v} {o}."
        cites = rng.sample(source_ids, k=rng.randint(1, 3))
        (root / "claims" / f"{cid}.yaml").write_text(
            f"id: {cid}\n"
            f"text: {text}\n"
            f"type: fact\n"
            f"status: stable\n"
            f"confidence: {round(rng.uniform(0.6, 1.0), 2)}\n"
            f"evidence:\n" + "".join(f"  - {sid}\n" for sid in cites)
        )

    print(f"generated {args.claims} claims under {root}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
