# examples/

Real-shaped sample KBs that show what vouch looks like in use.

Each subdirectory is a self-contained `.vouch/`-style tree (without the
leading dot — `vouch/`, so it's visible in the GitHub UI). Copy the
contents into a real `.vouch/` directory at your project root to play
with the data.

| Example | Topic | Size |
|---|---|---|
| [tiny/](tiny/) | A four-claim KB about a hypothetical auth design | 4 claims, 1 page, 2 sources |
| [decision-log/](decision-log/) | What a team's decision log looks like as vouch claims | 6 claims, 3 pages |

## Trying an example

```bash
mkdir my-test && cd my-test
git init
cp -r /path/to/vouch/examples/tiny/vouch ./.vouch
vouch status
vouch search auth
vouch pending           # empty — examples ship as already-approved
```

The example KBs ship with everything already in `claims/`, `pages/`,
etc. — they're "post-approval" snapshots. There are no `proposed/`
entries because proposals are local-only by nature.

## Anti-examples

We deliberately don't ship a "200k claims, every entity in the world"
example. Those are benchmark fixtures, not learning material. See
[benchmarks/](../benchmarks/) for synthesizing those.
