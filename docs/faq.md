# FAQ

Questions we keep getting. If you have a new one, please file an
issue with the `faq:` label.

---

**Why a review gate? Other tools just store whatever the agent says.**

Because LLM agents are bad at remembering things accurately, and a KB
that stores hallucinations isn't a KB — it's a transcript of confusion.
The whole bet of vouch is that the human-in-the-loop cost of
approving is *worth* the protection from drift. See
[VEP-0001](../proposals/VEP-0001-review-gate.md) for the full case.

---

**Can I use vouch without an LLM agent?**

Yes. The `vouch propose-*` CLI commands work fine from a shell. The
KB is plain YAML and markdown; you can hand-edit if you want. Agents
just make filling it up faster.

---

**How does vouch compare to mem0 / Letta / LLM-Wiki tools?**

Three differences, in order of importance:

1. **Review gate.** Other tools accept whatever the agent writes. We
   require explicit approval.
2. **Files in your repo.** Other tools store in a service or a
   sidecar database. We use plain text in `.vouch/`. Your VCS is the
   audit log.
3. **Citations required.** Other tools treat sources as optional
   metadata. We treat a claim without evidence as a validation error.

Trade-off: vouch is slower out of the box, because there's a human in
the path. If "agent writes, agent reads" is your bar, mem0 will feel
faster. If "knowledge that's safe to act on" is the bar, vouch is the
tool.

---

**Can the agent approve its own proposals?**

By default, no. Set `review.approver_role: trusted-agent` in
`config.yaml` to allow it; this is for fully autonomous setups where
you've decided the audit log alone is sufficient. The default
configuration blocks self-approval as `forbidden_self_approval`.

---

**What's the storage model — am I going to outgrow it?**

Plain text files plus a SQLite FTS5 index. We've tested up to ~10k
claims comfortably; beyond that, search latency starts to climb (still
under 100ms, but it's measurable). For ~100k claims you'll probably
want the embedding backend that lands in 0.1.

If your KB is going to be in the millions of claims, vouch is probably
the wrong tool — and your "KB" is probably a search engine.

---

**Why MCP *and* JSONL?**

Different consumers. MCP is the right transport for LLM hosts
(Claude Code, Cursor, Codex). JSONL is the right transport for shell
scripts, CI jobs, and people learning the protocol from a terminal.
Both expose the same `kb.*` surface; the only thing that differs is
framing. See [transports.md](transports.md).

---

**Can I run vouch as a service?**

Not officially, today. The transports are stdio-based on purpose —
they assume the consumer is the parent process. If you want a network
listener, HTTP is on the roadmap for 0.1. Until then, wrapping
`vouch serve --transport jsonl` in your own auth/networking layer is
your responsibility.

---

**What if I want to use a different file format — JSON, TOML, anything?**

You can't, today. YAML for structured artifacts; markdown with YAML
frontmatter for pages. That's a deliberate constraint: the formats
were picked so the KB diffs cleanly in PRs and is human-editable
without a tool.

If you have a real use case (e.g. "we need JSON because our build
system can't parse YAML"), file a VEP. We're not religious about it,
just unconvinced it's worth the surface area.

---

**Will vouch sync across multiple `.vouch/` directories?**

Not today. Use [bundles](bundles.md) for snapshot transfer. Live sync
between independent KBs is on the roadmap (0.2) and needs a merge
strategy that doesn't silently drop information. See
[multi-agent.md](multi-agent.md) for what works today.

---

**Why don't approved claims have a public-facing URL?**

vouch is a *library* and a *CLI*, not a wiki. If you want a public
URL surface, drive a static site generator from `.vouch/pages/` and
`.vouch/claims/` (they're plain markdown/YAML — easy). We don't ship
that ourselves because every team wants a different look.

---

**Does vouch ship to PyPI?**

Not yet (pre-1.0). Install from source. PyPI publication will land
with the 0.1 release.

---

**Can I delete the audit log?**

You *can* — `audit.log.jsonl` is a normal file — but you shouldn't.
The log is the *only* irrefutable record of what was decided. Once
you delete history, the rest of the design loses meaning. Rotation
(compressing old segments) is fine; deletion is a footgun.

---

**Is there a hosted vouch?**

No. Not planned. vouch is small and local on purpose. A hosted
multi-tenant version would be someone else's product.

---

**Is the spec stable?**

Pre-1.0, no. The on-disk layout might shift, methods might be added,
some might be renamed. We commit to:

- Documenting every breaking change in `CHANGELOG.md`.
- Providing a `vouch migrate` for any on-disk format change.
- Freezing both the layout and the method surface at 1.0.

---

**How do I report a security issue?**

[SECURITY.md](../SECURITY.md). Not as a public issue.
