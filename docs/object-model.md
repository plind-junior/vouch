# Object model — for users

This is the human-friendly version of [../SPEC.md §2](../SPEC.md#2-object-model).
If you want the field-by-field schema, read the spec; if you want to
*understand* the model, read this.

## The shape of a KB

A vouch KB is six kinds of objects, plus the audit log:

```
              ┌──── Source ───────────────┐
              │  immutable input bytes,    │
              │  content-addressed sha256  │
              └────────────┬──────────────┘
                           │  cited by
                           ▼
              ┌──── Claim ────────────────┐
              │  atomic assertion,         │
              │  must cite ≥ 1 source/ev   │
              └────────────┬──────────────┘
                           │  referenced by
                           ▼
              ┌──── Page ─────────────────┐
              │  narrative markdown that   │
              │  weaves claims together    │
              └───────────────────────────┘

              ┌──── Entity ───────────────┐
              │  typed named thing         │
              │  (service, person, repo…)  │
              └────────────┬──────────────┘
                           │
                           ▼
              ┌──── Relation ─────────────┐
              │  typed edge between two    │
              │  ids (uses, supersedes…)   │
              └───────────────────────────┘
```

## Sources are the foundation

A **Source** is "the bytes that something was said in" — a meeting
note, a PR description, a transcript, a URL snapshot, a commit
message. vouch identifies sources by sha256 of the content. Re-adding
the same content gives you the same id.

When a source is large or external (a YouTube transcript, a public
URL), you can register *just the metadata* — vouch records the
locator and the hash you saw at capture time, without copying bytes
locally.

**Evidence** is more specific: a *pointer into* a source. "Lines
20-25 of meeting-notes.md" or "0:14:23 in the recording". Claims can
cite either Sources or Evidence.

## Claims are atomic

A **Claim** is the smallest statement worth citing or contradicting.
Examples:

- ✅ "Auth uses JWTs in the Authorization header." — one fact, one
  citation, easy to verify.
- ❌ "Auth uses JWTs, we use Postgres, and on-call is 24/7." — three
  claims jammed together. Split.

A claim has:

- **text** — one sentence.
- **type** — fact / decision / preference / workflow / observation /
  question / warning.
- **status** — working (draft) / actionable / stable (the default
  durable state) / contested (two stable claims disagree) / superseded
  (a newer claim replaced this one) / archived / redacted.
- **confidence** — 0.0 to 1.0. Default 0.7. Be honest; 1.0 is
  suspicious.
- **evidence** — one or more Source or Evidence ids. **Required.**
  A claim without evidence is rejected at the gate.

## Pages are narrative

A **Page** is maintained markdown. Use pages when:

- You want a *write-up*, not a list of disconnected facts.
- You want one URL/file to land on when someone says "tell me about
  auth".
- You're producing a decision record that needs prose explaining the
  trade-offs.

Pages reference claims by id. They have YAML frontmatter for metadata
(claims, entities, sources, tags) and plain GitHub-flavoured markdown
for the body.

## Entities and Relations form the graph

An **Entity** is a typed named thing: a person, a service, a repo, a
concept, an incident. Entities anchor claims — instead of saying
"about Postgres" via tags, you say `entities: [postgres]` and the
graph knows.

A **Relation** is a typed edge between two ids: `service-api uses
postgres`, `claim-x supersedes claim-y`, `decision-z implements
rfc-12`. Relations are themselves objects with their own ids, so you
can cite *the connection*.

You don't have to use entities and relations. A small KB does fine
with just Claims and Pages. They start paying off around 50+ claims,
when "find everything about X" stops being easy via search alone.

## Sessions and Crystallisation

A **Session** is one work block an agent had. It opens with
`kb.session_start`, closes with `kb.session_end`, and bundles every
proposal the agent filed during that block.

`kb.crystallize` looks at a closed session and produces a
session-summary page. The agent's proposals are listed; the durable
parts get promoted into reviewable form. This is how an hour of agent
work compresses into a coherent record without the human having to
read every individual proposal.

## Proposals — the review gate

A **Proposal** is what the agent files instead of writing directly.
It contains the would-be artifact in its `payload`, plus
`proposed_by`, `rationale`, and a `status` (`pending` → `approved` or
`rejected`).

Proposals live in `.vouch/proposed/` (gitignored) until decided, then
move to `.vouch/decided/` (committed). The durable artifact —
claims/, pages/, etc. — is only written on approve.

See [review-gate.md](review-gate.md) for the state machine.

## Audit log

Every mutation in the KB emits one line in `.vouch/audit.log.jsonl`.
Source registration, proposal creation, approval, rejection,
supersession, archival — all of it. The log is committed and
append-only.

This is what makes vouch *auditable*: not the review gate alone, but
the gate plus a complete history of what was decided when by whom.

## Things that aren't objects

vouch deliberately doesn't have:

- **Tags as first-class.** Tags are strings on objects, not their own
  records. If a tag matters enough to be cited, it should be an
  Entity.
- **Folders or namespaces.** The flat directory layout is the storage,
  not the user-facing organisation. Pages and entities are how you
  group things.
- **Comments on claims.** A comment that argues with a claim is
  itself a claim — file it, cite it, mark `contradicts`.

These omissions are intentional. If you find yourself wanting one of
them, please open an issue; we're listening.
