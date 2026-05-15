# templates/

Starter files for each artifact in a vouch KB. Hand-editable; meant to
be copied into a real `.vouch/` directory and tweaked.

The CLI's `vouch propose-*` commands also produce these shapes (and
validate them), so for normal use you don't need these — they're for:

- Bulk-loading an existing decision log into vouch.
- Producing a proposal manually when the agent isn't available.
- Onboarding: showing newcomers what each artifact looks like before
  they touch the CLI.

## Files

| Template | Goes in | Notes |
|---|---|---|
| [claim.template.yaml](claim.template.yaml) | `.vouch/claims/` | Required: `id`, `text`, `evidence` |
| [page.template.md](page.template.md) | `.vouch/pages/` | YAML frontmatter + markdown body |
| [entity.template.yaml](entity.template.yaml) | `.vouch/entities/` | Required: `id`, `name`, `type` |
| [relation.template.yaml](relation.template.yaml) | `.vouch/relations/` | Required: `id`, `source`, `relation`, `target` |
| [evidence.template.yaml](evidence.template.yaml) | `.vouch/evidence/` | Required: `id`, `source_id`, `locator` |
| [source.meta.template.yaml](source.meta.template.yaml) | `.vouch/sources/<sha>/meta.yaml` | Required: `id` (sha256), `type`, `locator` |
| [session.template.yaml](session.template.yaml) | `.vouch/sessions/` | Created by `kb.session_start`; this is the shape |
| [proposal.template.yaml](proposal.template.yaml) | `.vouch/proposed/` | Shape produced by `kb.propose_*` |
| [config.template.yaml](config.template.yaml) | `.vouch/config.yaml` | One per KB; created by `vouch init` |

## Validation

If you hand-edit these, run `vouch doctor` afterward. It catches
missing citations, dangling references, and source-hash drift.

If you write directly into `.vouch/claims/` etc. bypassing the
proposal flow, **the review gate didn't run.** That's fine for an
initial bulk import (you're acting as the approver of record), but
record it in `audit.log.jsonl` as a `bundle.import`-style event so
the history is honest.
