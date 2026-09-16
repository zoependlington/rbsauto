# Importing a term from FoodOn

This is the canonical procedure `pizza-importer` follows. It's written out here so a human can also do it by hand, and so the subagent spec (`.claude/agents/pizza-importer.md`) can stay short and just point here for detail.

## 1. Find the term

Search the [OLS](https://www.ebi.ac.uk/ols4/) API, scoped to FoodOn:

```
https://www.ebi.ac.uk/ols4/api/search?q=<label>&ontology=foodon
```

Look for an exact or near-exact label/synonym match. Note the `obo_id` (e.g. `FOODON:00001234`) and the full IRI (`http://purl.obolibrary.org/obo/FOODON_00001234`).

## 2. Verify the sense

Fetch the term's own record and check its definition and immediate parent. Food/ingredient labels are prone to homonym collisions (e.g. "ham" the meat vs. an unrelated sense) — the parent chain is usually enough to confirm you have the right one. If in doubt, run a second query on a distinguishing synonym.

## 3. Add the dependency

Append the full IRI to `src/ontology/imports/foodon_terms.txt`, one IRI per line. Never edit `src/ontology/imports/foodon_import.owl` directly — it's generated.

## 4. Regenerate

From `src/ontology`:

```bash
make imports/foodon_import.owl -B
```

## 5. Attach it in pizza-edit.owl (pizza-ontologist's step, not importer's)

If the imported term needs to sit as a subclass of something pizza-specific (e.g. the imported FoodOn "ham" term should be cross-referenced from our `PizzaTopping` hierarchy), add the axiom to `src/templates/subclasses.csv` rather than hand-editing `pizza-edit.owl`'s imports block, then run:

```bash
make components/subclasses.owl
```

## Common mistakes this procedure prevents

- **Guessing an ID** instead of looking it up — always causes either a 404 on regeneration or, worse, a silent wrong-term import.
- **Hand-editing `imports/`** — gets silently overwritten the next time anyone runs `make imports/foodon_import.owl -B`, so the change appears to "disappear" later for no obvious reason.
- **Skipping the FoodOn check entirely** and authoring a duplicate local class for something that already has a perfectly good upstream definition.
