![CI](https://img.shields.io/badge/CI-robot%20reason-blue)
![Demo](https://img.shields.io/badge/status-demo%20repo-orange)

# 🍕 Pizza Ontology

A tiny, deliberately toy OWL ontology of pizzas, bases, and toppings — used here as a **worked example of AI-agent-driven ontology maintenance**, modeled directly on the workflow [EBISPOT/efo](https://github.com/EBISPOT/efo) uses for the real-world Experimental Factor Ontology.

This repo is not trying to be a serious pizza ontology (Manchester already wrote the canonical one for teaching OWL). It exists to show, end-to-end, **how a Claude Code agent can take a GitHub issue and turn it into a reviewable pull request against an ontology**, including:

- reading a term request from an issue,
- researching/justifying the term,
- importing a term from an external ontology when one already exists upstream,
- editing the OWL file correctly (IDs, axioms, definitions, provenance),
- running the OWL reasoner to check nothing broke,
- and opening a PR with a clear, checkable summary.

If you want to bootstrap something similar for your own ontology, everything domain-specific lives in `CLAUDE.md`, `.claude/agents/`, and `docs/` — swap the pizza content out and the automation pattern travels with it.

## How it works

1. Someone opens an issue using the **New pizza term** template (e.g. "add Hawaiian Pizza").
2. A maintainer (or the reporter, if trusted) comments `@claude handle this` — or just assigns the issue to `claude`.
3. GitHub Actions fires `anthropics/claude-code-action`, which loads `CLAUDE.md` as its orchestration instructions.
4. Claude acts as **orchestrator**: it triages the ticket, dispatches the relevant specialist subagent(s) defined in `.claude/agents/`, edits `src/ontology/pizza-edit.owl`, runs `robot reason` to validate, commits to a branch, and opens a PR referencing the issue.
5. A human reviews and merges.

See `docs/agents-documentation/system-overview.md` for the full architecture, and `CLAUDE.md` for the orchestrator's actual playbook.

## Repo layout

```
.claude/agents/          # subagent specs (curator, importer, ontologist)
.github/workflows/       # qc.yml (full ODK QC, Docker-based) + the Claude Code agent trigger
.github/ISSUE_TEMPLATE/  # structured term-request issue form
docs/                    # architecture docs + domain reference docs for the agents
src/
  templates/             # ROBOT template CSVs (e.g. cross-ontology subclass axioms)
  metadata/              # ontology metadata used by the ODK build
  sparql/                # QC queries and reports used by the Makefile
  ontology/
    pizza-edit.owl       # the editors' file — humans and agents both edit this
    pizza-odk.yaml       # ODK project configuration
    Makefile             # ODK-generated — do not hand-edit; see pizza.Makefile
    pizza.Makefile       # project-specific overrides go here instead
    imports/
      foodon_terms.txt   # curated seed list of FoodOn IRIs to import (hand-edited)
      foodon_import.owl  # generated import module — never hand-edit
    components/
      subclasses.owl     # generated from src/templates/subclasses.csv — never hand-edit
```

## Ontology structure (what's actually in it)

A minimal but real classification, deliberately mirroring the Manchester Pizza tutorial:

- `Pizza` ⊐ `PizzaBase` (`ThinAndCrispyBase`, `DeepPanBase`) and `PizzaTopping`
  (`CheeseTopping`, `MeatTopping`, `VegetableTopping`, `SeafoodTopping`, each with a couple of leaf toppings)
- Named pizzas (`MargheritaPizza`, `PepperoniPizza`, …) defined via `hasBase`/`hasTopping` restrictions
- `VegetarianPizza` is an **equivalent-class (defined)** concept — `Pizza and not (hasTopping some (MeatTopping or SeafoodTopping))` — so the reasoner actually has something non-trivial to classify. Run `robot reason` and watch pizzas get auto-classified as vegetarian or not based on their toppings.

## Running it locally

You'll need [ROBOT](https://robot.obolibrary.org/) (`brew install robot` or use the [obolibrary/odk](https://github.com/INCATools/ontology-development-kit) Docker image) on your PATH.

```bash
cd src/ontology
make normalize_src              # normalize formatting after any edit
robot reason -i pizza-edit.owl -r ELK -o /tmp/pizza-reasoned.owl   # validate + classify
```

## Setting up the agent yourself

1. In a Claude Code terminal, run `/install-github-app` against your fork/copy of this repo (repo admin required). This installs the Claude GitHub App and adds the `ANTHROPIC_API_KEY` secret automatically. Manual steps are in `docs/agents-documentation/CLAUDE-CODE-SETUP.md`.
2. Open an issue with the **New pizza term** template.
3. Comment `@claude handle issue #<N>` (or assign the issue to the `claude` bot user, which the workflow also watches for).
4. Watch the Actions tab — Claude will triage, dispatch subagents, and open a PR.

## Credit

Architecture pattern adapted from [EBISPOT/efo](https://github.com/EBISPOT/efo)'s Claude Code multi-agent orchestration setup. Repo scaffolding style follows the [Ontology Development Kit (ODK)](https://github.com/INCATools/ontology-development-kit) conventions used across OBO Foundry ontologies.

## License

Ontology content: [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code/config: MIT (see `LICENSE`).
