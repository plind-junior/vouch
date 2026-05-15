# Bundles — exporting and importing KBs

A *bundle* is a portable, verifiable snapshot of a vouch KB. Use them
to share knowledge between repos, hand a KB to a new teammate, or
back up to long-term storage.

## What's in a bundle

A `tar.gz` containing:

- `manifest.json` — version, generated-at, file list with per-file sha256
- `config.yaml`
- `claims/`, `pages/`, `entities/`, `relations/`, `evidence/`,
  `sources/`, `sessions/`, `decided/`

What's **not** in a bundle:

- `proposed/` — proposals are drafts; they don't travel
- `state.db` — derived; rebuild after import
- `audit.log.jsonl` — local history of one instance; doesn't merge
  cleanly

## Export

```bash
vouch export --out kb.tar.gz
# wrote kb.tar.gz (142 files, 386 KB)
```

`vouch export-check` verifies the tarball matches its manifest before
you ship it:

```bash
vouch export-check kb.tar.gz
# ok: 142/142 files match
```

## Import (the safe way)

Imports default to *check first, apply later*.

```bash
vouch import-check kb.tar.gz
# new:        87
# conflict:   3
# identical: 52
```

What each bucket means:

- **new** — the file doesn't exist in your KB. Will be added.
- **conflict** — the file exists at the same path with different
  bytes. Will be skipped, overwritten, or fail, depending on
  `--on-conflict`.
- **identical** — same path, same bytes. No-op.

Then apply:

```bash
vouch import-apply kb.tar.gz --on-conflict skip
# imported: 87, skipped: 3, overwritten: 0
```

Conflict resolution:

- `skip` (default) — keep your version of every conflict.
- `overwrite` — replace your version with the bundle's. Destructive.
  Make a git commit first.
- `fail` — abort the entire import on first conflict. Useful in CI.

After importing, rebuild the index:

```bash
vouch index
```

…and review the audit log, which gets a `bundle.import` event with
the file path.

## Manifest integrity

`manifest.json` carries:

```json
{
  "version": "0.1",
  "generated_at": "2026-05-17T10:00:00Z",
  "kb_name": "auth-kb",
  "vouch_version": "0.0.1",
  "files": [
    {"path": "claims/auth-uses-jwt.yaml", "sha256": "abc…", "bytes": 412},
    ...
  ]
}
```

Every byte that the bundle claims to ship is hashed. `import-check`
re-hashes on read and refuses to apply a tampered or truncated
bundle. The schema is at
[../schemas/bundle.manifest.schema.json](../schemas/bundle.manifest.schema.json).

## What bundles don't merge

Bundles are *additive*. They can:

- ✅ Add new claims, pages, entities, relations, sources.
- ✅ Carry the `decided/` history that accompanies them.

They cannot:

- ❌ Merge two audit logs into one. Each instance has its own log.
- ❌ Reconcile contradicting decisions automatically. If both KBs
  approved different versions of the same claim id, `import-check`
  flags it as conflict and you pick.
- ❌ Transfer pending proposals. By design — those are draft state.

## Use cases

**Onboarding a new repo to an existing KB.** Bundle the source KB,
import on the new side, commit the imported `.vouch/`, you're done.

**Splitting a KB.** Use git: copy the repo, `rm` the parts you don't
want from `claims/` / `pages/` / etc., commit, run `vouch doctor` to
catch dangling references.

**Federating two teams.** Bundle each side, import the other side's
into yours with `--on-conflict fail`. Conflicts become a checklist of
"who's right, you or me?" — exactly the conversation you needed to
have anyway.

## Why no merging tool

A merge command would have to make trust decisions: which side's
version of a claim is canonical? Better to surface conflicts and let
humans decide explicitly. A `vouch merge` that "just works" would
silently lose information.
