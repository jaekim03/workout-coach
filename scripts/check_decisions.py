#!/usr/bin/env python3
"""Decision checker (DESIGN §11).

Fails if:
  1. an engine module contains a numeric literal that is not from config.py
     (0, 1 and subscript indices are exempt);
  2. a config.py constant has no `# D-<n>` comment naming a DECISIONS.md entry;
  3. a one-way entry is new as locked, became locked, or changed while locked
     since BASE without a new `Answered:` line, which /decisions writes.
     (Skipped when DECISIONS.md does not exist at BASE: the first import.)
  4. a migration that exists at BASE was edited or removed.

    check_decisions.py [--base REF]
"""
from __future__ import annotations

import argparse
import ast
import io
import re
import subprocess
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = "DECISIONS.md"
CONFIG = Path("src/coach/config.py")
ENGINE_DIR = Path("src/coach/engine")
MIGRATIONS_DIR = "src/coach/migrations"

ENTRY_HEADING = re.compile(r"^## (D-\d+): .+$", re.MULTILINE)
ANY_HEADING = re.compile(r"^## .*$", re.MULTILINE)
ANSWERED = re.compile(r"^\d{4}-\d{2}-\d{2} via /decisions( \(\d+\))?$")
FIELD = re.compile(r"^(Status|Type|Choice|Rationale|Answered): *(.*)$", re.MULTILINE)
DECISION_ID = re.compile(r"\bD-\d+\b")
STATUSES = {"locked", "open"}
TYPES = {"one-way", "two-way"}
REQUIRED_FIELDS = ("Status", "Type", "Choice", "Rationale")
EXEMPT_LITERALS = (0, 1)


@dataclass(frozen=True)
class Entry:
    id: str
    text: str
    fields: dict[str, str]


def parse_decisions(text: str) -> tuple[dict[str, Entry], list[str]]:
    entries: dict[str, Entry] = {}
    errors: list[str] = []
    headings = list(ENTRY_HEADING.finditer(text))
    for match in ANY_HEADING.finditer(text):
        if not ENTRY_HEADING.fullmatch(match.group()):
            errors.append(f"malformed entry heading: {match.group()!r}")
    for i, match in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        body = text[match.start():end].strip()
        pairs = FIELD.findall(body)
        fields = dict(pairs)
        entry_id = match.group(1)
        if len(pairs) != len(fields):
            errors.append(f"{entry_id}: a field appears more than once")
        if entry_id in entries:
            errors.append(f"{entry_id}: duplicate entry")
        for name in REQUIRED_FIELDS:
            if name not in fields:
                errors.append(f"{entry_id}: missing field {name}")
        if fields.get("Status") not in STATUSES:
            errors.append(f"{entry_id}: Status must be locked or open")
        if fields.get("Type") not in TYPES:
            errors.append(f"{entry_id}: Type must be one-way or two-way")
        entries[entry_id] = Entry(entry_id, body, fields)
    return entries, errors


def numeric_literals(source: str) -> list[tuple[int, object]]:
    """Return (line, value) for each numeric literal that must come from config."""
    tree = ast.parse(source)
    index_nodes = {
        id(node)
        for sub in ast.walk(tree)
        if isinstance(sub, ast.Subscript)
        for node in ast.walk(sub.slice)
    }
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or id(node) in index_nodes:
            continue
        value = node.value
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if value in EXEMPT_LITERALS:
            continue
        found.append((node.lineno, node.col_offset, value))
    return [(line, value) for line, _, value in sorted(found, key=lambda f: f[:2])]


def config_constants(source: str) -> list[tuple[str, int, set[str]]]:
    """Return (name, line, decision ids) for each module-level UPPER_CASE constant."""
    comments: dict[int, str] = {}
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type == tokenize.COMMENT:
            comments[tok.start[0]] = tok.string
    lines = source.splitlines()

    constants = []
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        names = [t.id for t in targets if isinstance(t, ast.Name) and t.id.isupper()]
        if not names:
            continue
        span = list(range(node.lineno, (node.end_lineno or node.lineno) + 1))
        above = node.lineno - 1
        if above >= 1 and lines[above - 1].lstrip().startswith("#"):
            span.append(above)
        ids = {
            d for line in span for d in DECISION_ID.findall(comments.get(line, ""))
        }
        constants.extend((name, node.lineno, ids) for name in names)
    return constants


def _locked_one_way(entry: Entry | None) -> bool:
    return (
        entry is not None
        and entry.fields.get("Status") == "locked"
        and entry.fields.get("Type") == "one-way"
    )


def locked_changes(base: dict[str, Entry], head: dict[str, Entry]) -> list[str]:
    errors = []
    for entry_id, old in base.items():
        if _locked_one_way(old) and entry_id not in head:
            errors.append(f"{entry_id}: locked one-way entry was removed")
    for entry_id, new in head.items():
        old = base.get(entry_id)
        if not _locked_one_way(new):
            if _locked_one_way(old):
                errors.append(
                    f"{entry_id}: locked one-way entry was reopened or retyped "
                    "(answer it again with /decisions)"
                )
            continue
        if _locked_one_way(old) and old.text == new.text:
            continue
        answered = new.fields.get("Answered", "")
        if not ANSWERED.fullmatch(answered) or (
            old is not None and answered == old.fields.get("Answered")
        ):
            errors.append(
                f"{entry_id}: one-way entry was locked or changed without a new "
                "'Answered: <YYYY-MM-DD> via /decisions' line (run /decisions)"
            )
    return errors


def run(root: Path, base_decisions: str | None) -> list[str]:
    decisions_path = root / DECISIONS
    if not decisions_path.exists():
        return [f"{DECISIONS} is missing"]
    entries, errors = parse_decisions(decisions_path.read_text())

    engine_dir = root / ENGINE_DIR
    for module in sorted(engine_dir.rglob("*.py")) if engine_dir.exists() else []:
        rel = module.relative_to(root)
        for line, value in numeric_literals(module.read_text()):
            errors.append(
                f"{rel}:{line}: numeric literal {value!r} must be a config.py constant"
            )

    config_path = root / CONFIG
    if config_path.exists():
        for name, line, ids in config_constants(config_path.read_text()):
            if not ids:
                errors.append(f"{CONFIG}:{line}: {name} has no # D-<n> comment")
            for missing in sorted(ids - entries.keys()):
                errors.append(
                    f"{CONFIG}:{line}: {name} cites {missing}, "
                    f"which is not in {DECISIONS}"
                )

    if base_decisions is not None:
        base_entries, _ = parse_decisions(base_decisions)
        errors.extend(locked_changes(base_entries, entries))
    return errors


def changed_migrations(base: str, root: Path = ROOT) -> list[str]:
    """Migrations that exist at `base` and were edited, renamed or deleted since.

    A merged migration has already run against a real database, so it changes
    stored-data shape (one-way, DESIGN §11): add a new migration instead.
    """
    out = subprocess.run(
        ["git", "diff", "--name-only", "--no-renames", "--diff-filter=MDT",
         base, "HEAD", "--", MIGRATIONS_DIR],
        cwd=root, check=True, capture_output=True, text=True,
    ).stdout
    return [f"{name}: a merged migration must not change" for name in out.split()]


def read_at(ref: str) -> str | None:
    """DECISIONS.md at `ref`, or None if the file did not exist there."""
    subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        cwd=ROOT, check=True, capture_output=True,
    )
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISIONS}"], cwd=ROOT, capture_output=True, text=True
    )
    return result.stdout if result.returncode == 0 else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", metavar="REF")
    args = parser.parse_args(argv)

    try:
        base = read_at(args.base) if args.base is not None else None
    except subprocess.CalledProcessError:
        print(f"check_decisions: base {args.base!r} is not a commit", file=sys.stderr)
        return 2
    errors = run(ROOT, base)
    if args.base is not None:
        errors.extend(changed_migrations(args.base))
    for error in errors:
        print(f"check_decisions: {error}", file=sys.stderr)
    if errors:
        return 1
    print("check_decisions: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
