# Contributing

## Requesting a term (the normal path)

Open an issue with the **New pizza term** template. Then either:

- comment `@claude handle issue #<N>` to have the agent do the whole thing end-to-end and open a PR, or
- do it by hand (see below) if you'd rather.

## Doing it by hand

1. `git fetch origin main && git checkout -b issue-N origin/main`
2. Check FoodOn first if you're adding an ingredient/topping — see `docs/Import_terms_from_another_ontology.md`. Don't hand-author a class that duplicates an importable FoodOn term.
3. Edit `src/ontology/pizza-edit.owl`. Mint new IDs by hand only if you're assigning them permanently — otherwise use the `PIZZA_099xxxx` temporary range and let `.github/workflows/allocate-definitive-ids.yml` assign the real one after merge.
4. From `src/ontology`: `make normalize_src`, then `robot reason -i pizza-edit.owl -r ELK` and confirm no unsatisfiable classes.
5. Commit, push, open a PR referencing the issue.

## House rules (same ones the agent follows — see `CLAUDE.md`)

- `src/ontology/imports/*_import.owl` is generated. Never hand-edit it; edit `src/ontology/imports/*_terms.txt` and regenerate.
- Named pizzas need explicit `hasTopping`/`hasBase` restrictions for everything they're described as having.
- Every new class needs a label and a definition (`obo:IAO_0000115`).
- Work on a branch, never commit directly to `main`.

## Reporting a bug in the automation itself

If the agent did something wrong (bad axiom, wrong FoodOn match, skipped verification), open an issue describing what happened — that's useful signal for tightening `CLAUDE.md` or the relevant subagent spec in `.claude/agents/`.
