# Minimal ROBOT-based build, hand-written in the style of an ODK
# (Ontology Development Kit) generated Makefile. A real OBO-style ontology
# would generate this file rather than hand-write it -- see
# https://github.com/INCATools/ontology-development-kit. Kept simple and
# explicit here since it's the reference example, not production tooling.

ROBOT := robot
SRC := pizza-edit.owl

.PHONY: normalize_src reason convert

# Reformat pizza-edit.owl into a canonical, diff-friendly form. Run this
# after every manual or agent edit, before committing.
normalize_src:
	$(ROBOT) convert -i $(SRC) -o $(SRC) --format owl

# Syntax check only, no semantics.
convert:
	$(ROBOT) convert -vvv -i $(SRC) -o /tmp/pizza-syntax.owl

# Full OWL reasoning: consistency + unsatisfiable class check.
reason:
	$(ROBOT) reason -i $(SRC) -r ELK -o /tmp/pizza-reasoned.owl

# Regenerate the FoodOn import module from iri_dependencies/foodon_import.txt.
# `pizza-importer` is the only subagent that should trigger this.
imports/foodon_import.owl: iri_dependencies/foodon_import.txt
	$(ROBOT) extract \
		--method MIREOT \
		--input-iri http://purl.obolibrary.org/obo/foodon.owl \
		--lower-terms iri_dependencies/foodon_import.txt \
		--output imports/foodon_import.owl

# Cross-ontology subclass axioms declared in templates/subclasses.csv (e.g.
# attaching a pizza topping under an imported FoodOn ingredient class).
components/subclasses.owl: templates/subclasses.csv
	$(ROBOT) template \
		--template templates/subclasses.csv \
		--output components/subclasses.owl
