# Transports — for users

How to get vouch's `kb.*` surface in front of an agent (MCP) or a
script (JSONL).

For the framing details, see [../spec/transports.md](../spec/transports.md).
For host-specific wiring, see [../adapters/](../adapters/).

## When to use which

| You're connecting from… | Pick |
|---|---|
| Claude Code, Cursor, Codex, Continue, any MCP host | **MCP** (stdio) |
| Bash, Python script, CI job | **JSONL** |
| Another vouch instance | JSONL (today); HTTP (future) |
| A web UI you're writing | HTTP when it lands; until then, JSONL via a thin shim |

## MCP (stdio)

```bash
vouch serve                    # default
```

The server speaks MCP over stdin/stdout. Your host configures it as a
subprocess. Method `kb.search` is exposed as MCP tool `kb_search`
(dots aren't valid in MCP tool names).

### Resources

vouch also exposes read-only views as MCP resources:

| URI | content |
|---|---|
| `vouch://status` | `kb.status` result |
| `vouch://capabilities` | `kb.capabilities` |
| `vouch://pending` | pending proposals list |
| `vouch://claims/<id>` | one claim |
| `vouch://pages/<id>` | one page |

Hosts that browse resources can read those without tool calls.

### Prompts

Two named prompts you might wire up:

- `vouch.cite_this` — "register selection as evidence; propose a
  claim citing it"
- `vouch.crystallize_session` — "summarise this session's proposals
  into a page"

## JSONL (stdin/stdout)

```bash
vouch serve --transport jsonl
```

One JSON object per line, in and out.

### Request

```json
{"id": "r1", "method": "kb.search", "params": {"query": "jwt"}}
```

### Response

```json
{"id": "r1", "ok": true, "result": [...]}
```

### Smoke test

```bash
echo '{"id":"r1","method":"kb.capabilities"}' \
  | vouch serve --transport jsonl \
  | jq '.result.methods | length'
```

A two-digit number means the server is alive.

### Pipelining

You can send N requests, then read N responses. Order matches request
order. Useful when scripting a batch:

```bash
{
  echo '{"id":"a","method":"kb.list_pending"}'
  echo '{"id":"b","method":"kb.status"}'
} | vouch serve --transport jsonl
```

## Errors

Both transports surface errors with a `code` and `message`. Codes:

- `method_not_found` — typo, or the method doesn't exist on this version
- `missing_param` — a required parameter was absent
- `invalid_request` — the envelope was malformed
- `internal_error` — unexpected; check stderr, file a bug

MCP-specific errors come through MCP's native error mechanism; the
mapping is in [../spec/transports.md](../spec/transports.md).

## Identity

Both transports respect `VOUCH_AGENT`:

```bash
VOUCH_AGENT=alice-test vouch serve --transport jsonl
```

Every audit event records that as `actor`. Use it to distinguish
agents in multi-agent setups.

## A note on auth

vouch has none. Both transports are designed for parent-process
communication — the parent is the security boundary. If you put vouch
behind a network listener, **you** are responsible for auth on top.
Don't expose `vouch serve` to the open internet.
