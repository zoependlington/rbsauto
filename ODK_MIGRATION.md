# Migrating rbsauto to a real ODK build

This archive was produced by actually running `odk seed` (the real
Ontology Development Kit CLI, INCATools/odkcore) against your existing
`pizza-edit.owl`, then merging the result with everything in your repo
that isn't part of the ontology build itself. It replaces the
hand-written, ODK-styled Makefile with a genuine ODK-generated one.

## How to apply this

The safest way to apply this is a clean overwrite followed by a diff
review, since several files moved:

```sh
cd /path/to/your/local/clone/of/rbsauto
git checkout -b odk-migration

# Extract this archive over your working tree
tar xzf rbsauto-odk-migration.tar.gz --strip-components=1 -C .

# Remove the two old paths this migration retires
git rm -r --cached src/ontology/iri_dependencies src/ontology/templates 2>/dev/null

git add -A
git status   # review before committing
git commit -m "Migrate ontology build to real ODK"
git push -u origin odk-migration
```

Open a PR from that branch rather than pushing straight to `main`, and
read through the diff yourself before merging — this touches your build
system and several docs.

## What moved

| Old path | New path | Why |
|---|---|---|
| `src/ontology/iri_dependencies/foodon_import.txt` | `src/ontology/imports/foodon_terms.txt` | Real ODK convention: the curated seed list lives next to the generated import it produces, distinguished by the `_terms.txt` vs `_import.owl` suffix. |
| `src/ontology/templates/subclasses.csv` | `src/templates/subclasses.csv` | Real ODK's `TEMPLATEDIR` is `../templates` relative to `src/ontology`. Your `CLAUDE.md` already documented this path before the migration — the old hand-rolled Makefile hadn't caught up to it. |
| `src/ontology/Makefile` (hand-written) | `src/ontology/Makefile` (ODK-generated, do not edit) + `src/ontology/pizza.Makefile` (your override point) | ODK regenerates `Makefile` from `pizza-odk.yaml`; project-specific customization goes in `pizza.Makefile` instead so it survives a `sh run.sh update_repo`. |
| — | `.github/workflows/qc.yml` | New. ODK's own generated CI: runs `make test` inside the `obolibrary/odkfull` Docker image (full reasoning, SPARQL checks, ID-range validation) on every push/PR. This is separate from `claude.yml` — see below. |
| — | `src/ontology/pizza-odk.yaml`, `pizza-idranges.owl`, `src/metadata/`, `src/sparql/` | New. Config and support files the generated Makefile depends on for reports, ID-range checks, and metadata. |

## What changed in `.github/workflows/claude.yml`

The "Install ROBOT" step now also installs `odk-core` (pip), which
provides `odk-helper` — the generated Makefile's mirror-download step
(`$(IMPORTDIR)/foodon_import.owl`) calls it directly. ROBOT itself is
now pinned to `1.9.10`, the same version ODK's own `odkfull` image
currently ships, instead of "whatever curl grabs today."

The job still runs on a plain `ubuntu-latest` runner rather than inside
the `obolibrary/odkfull` container the way `qc.yml` does. That
container doesn't include the `gh` CLI, which the comment-posting fix
from earlier in this conversation depends on — so the split is
deliberate: `claude.yml` does day-to-day edit/import/normalize work
with a lighter toolchain, and `qc.yml` does full-strength validation
with the complete ODK toolchain via Docker on every PR, including ones
Claude opens.

## What changed in the docs

`README.md`, `CONTRIBUTING.md`, `CLAUDE.md`, both `.claude/agents/`
specs that touch imports, `docs/agents-documentation/system-overview.md`,
`docs/Import_terms_from_another_ontology.md`, and
`.github/copilot-instructions.md` all had their references to the old
`iri_dependencies/` and `src/ontology/templates/` paths updated to the
new ones.

## What was deliberately left alone

The root `README.md` and `CONTRIBUTING.md` are **your** files, not
ODK's generated versions — ODK's seed process also generates its own
generic versions of both, but those would have overwritten your
Claude-workflow-specific documentation with boilerplate, so they're
excluded from this archive.

## Before merging

- `src/ontology/pizza-idranges.owl` is new and currently has placeholder
  ID range values from the seed process — review it before relying on
  `make test`'s `validate_idranges` check.
- The full `make test` pipeline (via `qc.yml`) needs Docker and hasn't
  been run end-to-end against your actual FoodOn import yet — expect to
  debug the first CI run the way any new pipeline needs debugging.
- Delete `src/ontology/iri_dependencies/` and the old
  `src/ontology/templates/` directory once you've confirmed the new
  paths are working — the `git rm --cached` step above handles this if
  you're following the apply instructions exactly.
