# benchmarks/

Performance fixtures for vouch. The intent is to keep this minimal and
honest — vouch is not a search engine and we are not chasing milliseconds
against tools that are. But there are a few numbers that *do* matter:

- **Search latency** as the KB grows. FTS5 is fast on small KBs and
  fine on large ones; we want a published curve.
- **Proposal write latency.** This sits in the agent's hot loop. If it
  ever climbs past ~50ms on a warm SSD, something regressed.
- **Bundle import time.** Imports gate cross-team KB sharing; a 10k-claim
  bundle should land in seconds, not minutes.
- **Index rebuild time** at fixed KB sizes (1k / 10k / 100k claims).

## Status

Not implemented yet. See [ROADMAP.md](../ROADMAP.md) (0.3) for the
planned timeline. This README is a placeholder so we don't lose the
shape of what we want to measure.

## Planned layout

```
benchmarks/
├── README.md                  (you are here)
├── conftest.py                pytest-benchmark configuration
├── fixtures/
│   ├── gen_kb.py              synth a KB of N claims with realistic distributions
│   └── seed/                  pre-built fixture KBs (small, medium, large)
├── bench_search.py            kb.search latency at varying KB sizes
├── bench_propose.py           kb.propose_* write latency
├── bench_bundle.py            export + import + verify round-trips
└── bench_index_rebuild.py     kb.index_rebuild at varying sizes
```

Benchmarks live outside `tests/` so a regular `pytest` run doesn't
pull them in. The intended invocation is:

```bash
make bench         # not yet wired in the Makefile
# or:
pytest benchmarks/ --benchmark-only --benchmark-json=bench.json
```

## Methodology principles

- **Real disks.** No tmpfs benchmarks. The file-based design makes
  tmpfs misleadingly fast.
- **Cold and warm.** Report both; FTS5's first query after open is
  meaningfully slower than the second.
- **Reproducible fixtures.** `gen_kb.py` is seeded; the same seed
  produces the same KB.
- **Published environment.** Every benchmark run records CPU, RAM,
  disk model, and vouch version in the result JSON.

## What we explicitly are *not* benchmarking

- Semantic quality. That's a *correctness* concern, not a performance
  one; it belongs in [docs/](../docs/) and in the conformance suite
  (see ROADMAP 0.2).
- Comparison against other KB tools. We're not racing mem0. Speak for
  yourself, mem0.

## Contributing benchmarks

If you have a workload that stresses vouch in a way these don't
capture, please file a VEP describing the scenario rather than just
adding a `bench_*` file — we want the benchmark suite to be small and
intentional.
