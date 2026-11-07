"""Licence check (Phase 4 quality gate): reuse attribution must be complete.

Stdlib only. Verifies, for this MIT repo (a Markdown agent pack, no
Python package):
1. The root LICENSE file is the MIT licence.
2. Every source in scanner/SOURCES_MERGE_2026-11-07.md's licence table
   (Source | Licence | Commit inspected | Head date) has a non-empty
   Licence cell, and every other table in that file that carries a
   Licence column has no empty licence cell either.
3. No AGPL-licensed text is present. This is a heuristic, not a legal
   opinion: it fails on an AGPL licence file (COPYING/AGPL*), on the
   full "GNU Affero General Public License" text, or on a .py file
   claiming AGPL as its licence. Bare mentions of "AGPL-3.0" in
   attribution documents (SOURCES_MERGE, module headers saying "ideas
   only, AGPL-3.0") are attribution, not licensed content, and are
   reported as information, not failures.

Usage: python3 scripts/qa_licence.py [--root REPO_ROOT]
Exit 0 only when every check passes.
"""
import argparse
import re
from pathlib import Path

SOURCES_FILES = ["scanner/SOURCES_MERGE_2026-11-07.md"]
FORBIDDEN_TEXT = [
    "GNU Affero General Public License",
    "Licensed under the GNU Affero",
    "Affero General Public License",
]
FORBIDDEN_FILES = {"COPYING", "COPYING.AGPL", "AGPL-3.0.txt", "LICENSE.AGPL"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv"}
ATTRIBUTION_FILES = {"scanner/SOURCES_MERGE_2026-11-07.md",
                     "scripts/qa_licence.py"}


def licence_table_errors(text, rel):
    """Every Markdown table with a Licence column must have a non-empty
    licence cell in every data row."""
    errors = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if not lines[i].strip().startswith("|"):
            i += 1
            continue
        block = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            block.append(lines[i])
            i += 1
        if len(block) < 3:
            continue
        header = [c.strip().lower() for c in block[0].strip().strip("|").split("|")]
        if "licence" not in header and "license" not in header:
            continue
        col = header.index("licence") if "licence" in header else header.index("license")
        for row in block[2:]:
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) <= col or not cells[col]:
                errors.append(f"{rel}: licence table row missing a licence: "
                              f"{row.strip()[:100]}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",
                        default=str(Path(__file__).resolve().parent.parent))
    root = Path(parser.parse_args().root)
    errors, info = [], []

    licence = root / "LICENSE"
    if not licence.exists():
        errors.append("LICENSE file missing")
    elif "MIT License" not in licence.read_text(encoding="utf-8", errors="replace"):
        errors.append("LICENSE is not the MIT licence")

    for rel in SOURCES_FILES:
        path = root / rel
        if not path.exists():
            errors.append(f"SOURCES record missing: {rel}")
            continue
        errors.extend(licence_table_errors(
            path.read_text(encoding="utf-8", errors="replace"), rel))

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.name in FORBIDDEN_FILES:
            errors.append(f"AGPL licence file present: {rel}")
            continue
        if path.suffix.lower() not in (".py", ".md", ".txt", ".rst"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if str(rel) in ATTRIBUTION_FILES:
            if "AGPL-3.0" in text:
                info.append(f"{rel}: mentions AGPL-3.0 (attribution record)")
            continue
        for forbidden in FORBIDDEN_TEXT:
            if forbidden in text:
                errors.append(f"{rel}: contains AGPL licence text: {forbidden!r}")
        if path.suffix.lower() == ".py":
            if re.search(r"(?i)licensed under (the )?(GNU )?AGPL", text):
                errors.append(f"{rel}: .py file claims an AGPL licence")
            elif "AGPL" in text:
                info.append(f"{rel}: mentions AGPL (attribution comment)")

    for line in sorted(set(info)):
        print(f"INFO: {line}")
    if errors:
        print("FAIL: licence check found problems:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("PASS: licence check clean (MIT root, every SOURCES table row "
          "has a licence, no AGPL content)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
