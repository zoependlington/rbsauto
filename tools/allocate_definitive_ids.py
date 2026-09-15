#!/usr/bin/env python3
"""
Replace every temporary PIZZA_099xxxx ID in pizza-edit.owl with the next
definitive ID, tracked in tools/next_id.txt.

This mirrors EFO's allocate-definitive-ids workflow: agents mint temporary,
obviously-fake IDs during a PR (so two concurrent agent PRs can never clash),
and a human-triggered post-merge step assigns the real, permanent ID.

Usage: python3 tools/allocate_definitive_ids.py src/ontology/pizza-edit.owl
"""
import re
import sys
from pathlib import Path

NEXT_ID_FILE = Path(__file__).parent / "next_id.txt"
TEMP_ID_RE = re.compile(r"PIZZA_099\d{4}")


def next_id() -> str:
    current = int(NEXT_ID_FILE.read_text().strip())
    NEXT_ID_FILE.write_text(f"{current + 1}\n")
    return f"PIZZA_{current:07d}"


def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    path = Path(sys.argv[1])
    text = path.read_text()

    temp_ids = sorted(set(TEMP_ID_RE.findall(text)))
    if not temp_ids:
        print("No temporary PIZZA_099xxxx IDs found — nothing to do.")
        return

    mapping = {}
    for temp in temp_ids:
        mapping[temp] = next_id()
        print(f"{temp} -> {mapping[temp]}")

    for temp, definitive in mapping.items():
        text = text.replace(temp, definitive)

    path.write_text(text)
    print(f"Replaced {len(mapping)} temporary ID(s) in {path}.")


if __name__ == "__main__":
    main()
