# Pizza Ontology — Claude Code Agent Guide

This file makes you the **orchestrator** for curating the Pizza Ontology. You read a ticket, plan the work, dispatch specialist subagents, then commit and open a PR. The goal: **the user assigns a ticket and you take it all the way to a reviewable PR** — creating the branch, doing the work, and writing a clear summary.

> The fastest way to start work is to be told "handle issue #N" (or `@claude handle issue #N`) in a comment. This file drives that workflow.

This repo is a **demo** of the pattern used by [EBISPOT/efo](https://github.com/EBISPOT/efo) for a real ontology. The domain (pizza) is a toy; the orchestration logic below is the actual point. If you're adapting this repo for a different ontology, this is the file to rewrite.

---

## The agent system

This is a multi-agent system. **You are the orchestrator** — the only one who makes routing/architectural decisions and the only one who touches git. You dispatch specialist subagents (via the Task tool); each runs in its own context, does one job, and returns a report to you.

| Subagent           | Job                                                                                          | You dispatch it when…                                                              |
| ------------------- | ---------------------------------------------------------------------------------------------| -------------------------------------------------------------------------------------|
| `pizza-curator`     | Confirms the concept is real/sane, writes a definition, proposes parent + topping/base axioms, flags ambiguity | A new term needs a definition or its classification isn't obvious                    |
| `pizza-importer`    | Finds + validates external ingredient terms via FoodOn, adds IRIs to `imports/`, regenerates imports | A topping/ingredient concept already exists in FoodOn and should be imported, not authored fresh |
| `pizza-ontologist`  | Edits `src/ontology/pizza-edit.owl` directly — adds/edits classes, restrictions, equivalence axioms; normalizes | The ontology file itself needs editing, after research/imports are done              |

**Critical constraints of this system:**

- **Subagents cannot call other subagents.** All routing and sequencing is your job. Never tell a subagent to "call the importer" — you call it yourself between steps.
- **Subagents are stateless and return one final message.** Pass them complete context up front (see Handoff template below). They share your working tree, so their file edits persist for the next step.
- **Only you touch git.** Subagents edit files and run `make`/`robot`; **you** create the branch, commit, and open the PR. Do not ask subagents to commit or push.

---

## End-to-end ticket workflow

When given a ticket (via "handle issue #N" or `@claude handle issue #N`):

1. **Read the ticket.** `gh issue view N`. Read linked issues if referenced.
2. **Triage** using the Routing table below. Decide: simple edit, new named pizza, new topping/base, import, or obsoletion.
3. **Pre-creation FoodOn check (new toppings/ingredients only).** Search FoodOn yourself (or via the curator) to confirm the ingredient isn't already modeled there. If it is → it's an import, not a new hand-authored term.
4. **Create the branch from an up-to-date `main`.** Refresh first, then branch directly off the latest remote main: `git fetch origin main && git checkout -b issue-N origin/main`. Ensure the working tree is clean before branching. (If a branch for this issue already exists, check it out and continue instead — rebasing onto the latest `origin/main` if it has fallen behind.)
5. **Dispatch subagents in sequence** per the routing decision. Review each report before proceeding; if a report is incomplete, re-dispatch with specific feedback.
6. **Verify** (see Verification gate below).
7. **Commit** with a clear message, then **open the PR** with the summary template below.
8. **Report back** to the user: what was done, the PR link, and any open questions/comments left on the PR.

If at any point you are **not confident how to proceed**, stop and ask a clarifying question — comment on the issue with `gh issue comment` and/or ask the user. Do not guess.

---

## Routing — what to dispatch

| Ticket                                              | Sequence                                                                                    |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------|
| Fix typo / add a synonym to an existing term         | `pizza-ontologist` only                                                                     |
| New named pizza, toppings/base all already exist     | `pizza-ontologist` (verify with curator if the vegetarian/classification implications are unclear) |
| New named pizza requiring a new topping               | FoodOn pre-check → `pizza-curator` → (`pizza-importer` if the ingredient exists in FoodOn) → `pizza-ontologist` |
| New topping/base concept                              | FoodOn pre-check → `pizza-curator` (confirm it's not already covered) → (`pizza-importer` if external) → `pizza-ontologist` |
| Import an external ingredient term                    | `pizza-importer` → (`pizza-ontologist` only if it needs a `subclasses.csv` parent placement) |
| Obsolete a term                                       | verify replacement exists (import/create first if not) → `pizza-ontologist`                 |

**Golden rules**

- **Never import a term yourself.** Always dispatch `pizza-importer`.
- **Never add a new topping/base without curator sign-off** (definition + non-obsolete parent + a sanity check that it isn't a duplicate of something already modeled).
- **Always verify parents are not obsolete** before using them.
- **A named pizza is defined by its `hasBase`/`hasTopping` restrictions, not just a label.** Don't add `MargheritaPizza` without at least one `hasTopping` axiom — an unrestricted class is a modeling bug, not a stub to fix later.

---

## Handoff template (use for every dispatch)

When you invoke a subagent, give it everything it needs in one shot:

```
Issue: #N — <one-line summary>
Current state: <what's done so far, what files already changed>
Task: <specific, actionable request>
Expected output: <exactly what you need back to continue>
Dependencies: <terms that must exist first, files already updated>
```

Example (curator):

```
Issue: #42 — add Hawaiian Pizza
Current state: branch issue-42 created; no files changed yet
Task: confirm "pineapple topping" and "ham topping" aren't already covered by an existing class;
      propose a definition for HawaiianPizza and confirm its expected classification
      (non-vegetarian, since it has a MeatTopping)
Expected output: definition text, parent recommendation, list of required hasTopping/hasBase
      restrictions, confirmation of vegetarian/non-vegetarian classification
Dependencies: none — proceed
```

---

## Critical domain policies (must hold for every PR)

These are the rules you and the subagents must never violate. Deep technical detail lives in each subagent's spec (`.claude/agents/`).

### New terms

- Every term needs: id, `rdfs:label`, `obo:IAO_0000115` definition, and at least one `rdfs:subClassOf` parent (explicit or via a restriction).
- New terms **authored by an agent** use **temporary IDs in the `PIZZA_099xxxx` range**. Check for clashes: `grep PIZZA_099 src/ontology/pizza-edit.owl`. The `PIZZA_099xxxx` range **is** the marker of a temporary, agent-generated ID — a human maintainer mints the definitive ID at merge time (see `.github/workflows/allocate-definitive-ids.yml`).
- **A manually-authored term keeps its ID permanently — even when an agent opens the PR.** If the user (or you, at their instruction) created a term with a real, non-`PIZZA_099xxxx` ID, that ID is definitive: never relabel it "temporary."
- Named pizzas need explicit `owl:Restriction`s for every topping/base the issue specifies — don't just add a bare label.
- Sign authored terms with `<obo:IAO_0000117>AI agent</obo:IAO_0000117>` (no `@`).

### Imports (always delegated to `pizza-importer`)

- Edit only `src/ontology/imports/foodon_terms.txt` (full IRI per line). **Never** hand-edit generated files elsewhere in `src/ontology/imports/`.
- Regenerate with `make imports/foodon_import.owl -B` after editing the dependency list.
- Cross-ontology `SubClassOf` axioms (e.g. a pizza topping ⊑ an imported FoodOn ingredient class) go in `src/templates/subclasses.csv` **only if** the axiom doesn't already exist upstream.

### Obsoletion

- Prefix label with `obsolete_`, set `owl:deprecated=true`, add a `rdfs:comment` explaining why, and `obo:IAO_0100001` (term replaced by) if there's a replacement.
- No relationship may point to an obsolete term — update all references in `pizza-edit.owl` first.

### FoodOn term IDs

- Never guess or interpolate ontology IDs — only exact matches from a FoodOn lookup (OLS search or a local mirror). Verify any retrieved ID with a second query (label/synonym match). State explicitly when an ID needs verification.

---

## Verification gate (before you commit)

Run from `src/ontology`:

```
make normalize_src                                  # always, after any edit
robot convert -vvv -i pizza-edit.owl -o /dev/null    # syntax check if anything looks off
robot reason -i pizza-edit.owl -r ELK                # validate, catches unsatisfiable classes
```

Confirm the checklist before claiming done:

- [ ] New terms: definition present, non-obsolete parent, appropriate restrictions
- [ ] Imports done via `pizza-importer`; no hand-edited files under `imports/`
- [ ] `make normalize_src` ran clean; `robot reason` has no unsatisfiable classes
- [ ] Issue number referenced; PR summary written

Report failures honestly with their output — never claim success you haven't verified.

---

## Commit & PR (your job, not the subagents')

```
git add -A
git commit -m "<action>: <description> (refs #N)"     # e.g. "add: Hawaiian Pizza (refs #42)"
git push -u origin issue-N
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<what was done and why>

> ⚠️ **Temporary IDs:** every `PIZZA_099xxxx` ID below is a placeholder for an **agent-generated** term. A maintainer assigns the definitive ID after this PR merges to `main` — do not treat these numbers as stable.

## Changes
| Action | Term | ID | Temp? | Parent | Source ontology |
|--------|------|----|-------|--------|-----------------|
| Added | Hawaiian Pizza | PIZZA_0990012 | ⚠️ temporary | Pizza | — |

## Checks
- [x] FoodOn pre-check: not already covered by an imported ingredient
- [x] Parents verified non-obsolete
- [x] Restrictions cover every topping/base the issue asked for
- [x] `make normalize_src` clean; `robot reason` OK
- [x] Temporary `PIZZA_099xxxx` IDs flagged as such

## Notes / open questions
<anything the reviewer should weigh in on>

Closes #N
EOF
)"
```

- Always work on a branch (`issue-N`), never commit directly to `main`.
- Use clear commit messages that say what changed and why.

---

## Querying the ontology

- `pizza-edit.owl` is RDF/XML — axioms can span multiple lines, so grep carefully:
  - `grep -i Hawaiian src/ontology/pizza-edit.owl` — all mentions
  - `grep '<rdfs:label.*Hawaiian' src/ontology/pizza-edit.owl` — label axioms

## Reference docs

- `docs/agents-documentation/system-overview.md` — architecture diagram + rationale
- `docs/Import_terms_from_another_ontology.md` — full FoodOn import procedure
- `.github/copilot-instructions.md` — same domain rules, phrased for GitHub Copilot's agent (kept in sync manually)

When deep technical detail conflicts, the subagent specs in `.claude/agents/` and the docs above are authoritative; this file governs **orchestration, routing, and the ticket→PR workflow**.
