# System overview

## Why this shape

Ontology curation has a recurring structure that maps cleanly onto separate agent roles:

1. **Is this concept sound, and what's its definition?** — research/judgment work, no file mutation risk if it goes wrong. → `pizza-curator`
2. **Does this concept already exist upstream, in an ontology we can import from?** — a lookup + a very mechanical file edit (one line in `iri_dependencies/`, then regenerate). → `pizza-importer`
3. **Encode it correctly in OWL** — the highest-risk step (malformed axioms, ID clashes, broken restrictions). → `pizza-ontologist`

Splitting these into separate subagents gives each one a narrow tool surface and a narrow job, which makes their output easier to check — a report from `pizza-curator` is just prose you can read, `pizza-importer`'s diff is one line plus a regenerated file, and `pizza-ontologist`'s diff is the only place OWL axioms actually change.

The **orchestrator** (Claude running with `CLAUDE.md` loaded) is the only thing that:
- decides which subagents to dispatch and in what order,
- touches git (branch, commit, PR),
- talks to the user/issue thread.

This is the same shape [EBISPOT/efo](https://github.com/EBISPOT/efo) uses for the real Experimental Factor Ontology, just with the specifics swapped for a toy pizza domain.

## Request lifecycle

```
issue opened (New pizza term template)
        │
        ▼
"@claude handle issue #N"  ──────────────► GitHub Actions: anthropics/claude-code-action
        │                                          │
        │                                          ▼
        │                              Claude loads CLAUDE.md, reads issue via `gh issue view`
        │                                          │
        │                                          ▼
        │                              Triage: simple edit? new term? import? obsoletion?
        │                                          │
        │                    ┌─────────────────────┼─────────────────────┐
        │                    ▼                     ▼                     ▼
        │            pizza-curator          pizza-importer         pizza-ontologist
        │            (definition,           (FoodOn lookup,        (edits pizza-edit.owl,
        │             parent, restrictions)   iri_dependencies)      runs robot reason)
        │                    │                     │                     │
        │                    └─────────────────────┴─────────────────────┘
        │                                          │
        │                                          ▼
        │                       orchestrator: git commit, push, gh pr create
        │                                          │
        ▼                                          ▼
   issue thread  ◄───────────────────────  PR opened, summary posted
```

## Why temporary IDs

Two agent-driven PRs could theoretically be in flight at once, both minting new IDs. If they both grabbed the "next" permanent ID, merging either first would silently invalidate the other's ID. Using an obviously-temporary range (`PIZZA_099xxxx`) sidesteps this: any number of PRs can safely use IDs from that range simultaneously, since a human-triggered step reassigns permanent IDs one PR at a time, only after merge (`.github/workflows/allocate-definitive-ids.yml`).

## Why FoodOn imports specifically

Real ingredient/food-product terms (ham, mozzarella, pineapple) are exactly the kind of thing that's already been carefully modeled in a food ontology. Re-authoring them locally would mean re-doing that work worse, and — more importantly for the demo — it's the direct analogue of why EFO imports disease terms from MONDO and anatomy terms from UBERON rather than authoring its own: a good ontology maintenance workflow actively looks for reuse opportunities before creating new terms.
