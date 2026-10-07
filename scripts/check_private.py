#!/usr/bin/env python3
"""Privacy guard (DESIGN §13.2, D6).

Fails if an added or changed file could carry personal training information.

    check_private.py --staged              files staged for commit (pre-commit hook)
    check_private.py --commits BASE HEAD   every commit in BASE..HEAD, one by one (CI);
                                           an empty BASE means all of HEAD's history
    check_private.py FILE...               the named repo-relative files, from disk
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import posixpath
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Callable, Iterator

MAX_BYTES = 500 * 1024
SQLITE_HEADER = b"SQLite format 3\x00"
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
# Added, copied, modified, renamed, type-changed: everything but deletions.
DIFF_FILTER = "--diff-filter=ACMRT"

# Block rules are matched against the lower-cased path. The first group is the
# DESIGN §13.2 minimum list; the second is stricter than the spec (D-37).
# Keep .gitignore in sync.
BLOCKED_FILE_GLOBS = (
    "*.db", "*.sqlite", "*.sqlite3", "*.db-journal", "*.db-wal", "*.db-shm",
    "*.csv", "*.xlsx", "*.log", ".env", ".env.*",

    "*.db.*", "*.sqlite.*", "*.sqlite3.*", "*.csv.*", "*.log.*",
    "*.env", ".envrc", "*.sql", "*.dump", "*.bak", "*.tsv", "*.xls",
    "*.jsonl", "*.ndjson", "*.parquet", "*.pkl", "*.pickle", "*.ipynb",
    "*.zip", "*.gz", "*.tgz", "*.tar", "*.bz2", "*.xz", "*.7z",
    "*.png", "*.jpg", "*.jpeg", "*.heic", "*.gif", "*.webp", "*.mov", "*.mp4",
)
BLOCKED_DIRS = frozenset(
    {"data", "exports", "logs", "transcripts", "screenshots", "__pycache__", ".venv"}
)

# Allow rules are matched against the exact path, case included.
STRUCTURED_SUFFIXES = frozenset({".json", ".yaml", ".yml", ".csv"})
SEED_DIR = "seed"
FIXTURE_DIR = "tests/fixtures"
# Tool configuration the repo layout (§13.1) requires. Exact paths only (D-37).
ALLOWED_CONFIG = frozenset(
    {".github/workflows/ci.yml", ".pre-commit-config.yaml", ".claude/settings.json"}
)

# Schema migrations are the only .sql files allowed (D-37).
MIGRATION = re.compile(r"src/coach/migrations/\d{4}_[a-z0-9_]+\.sql")
# A migration changes structure; literal rows would be data (use INSERT ... SELECT
# to copy between tables).
SQL_LITERAL_ROWS = re.compile(rb"\bVALUES\b", re.IGNORECASE)

SYNTHETIC_MARKER = "# SYNTHETIC"
YAML_SYNTHETIC = re.compile(r"^synthetic:\s*true\s*$", re.MULTILINE)


def _is_synthetic(suffix: str, data: bytes) -> bool:
    text = data.decode("utf-8", errors="replace")
    first_line = text.splitlines()[0].strip() if text.strip() else ""
    if suffix == ".json":
        try:
            doc = json.loads(text)
        except ValueError:
            return False
        return isinstance(doc, dict) and doc.get("synthetic") is True
    if suffix in {".yaml", ".yml"}:
        return first_line == SYNTHETIC_MARKER or bool(YAML_SYNTHETIC.search(text))
    return first_line == SYNTHETIC_MARKER


def check_file(name: str, data: bytes) -> list[str]:
    """Return the reasons `name` (repo-relative, with content `data`) is not allowed."""
    path = PurePosixPath(name)
    lowered = PurePosixPath(name.lower())
    problems = []

    if path.is_absolute() or ".." in path.parts or posixpath.normpath(name) != name:
        return ["is not a normalized repo-relative path"]

    for glob in BLOCKED_FILE_GLOBS:
        if glob == "*.sql" and MIGRATION.fullmatch(name):
            continue
        if fnmatch.fnmatchcase(lowered.name, glob):
            problems.append(f"matches blocked pattern {glob}")
    for part in lowered.parts[:-1]:
        if part in BLOCKED_DIRS:
            problems.append(f"is inside blocked directory {part}/")

    if MIGRATION.fullmatch(name) and SQL_LITERAL_ROWS.search(data):
        problems.append("is a migration that inserts literal rows (VALUES)")
    if SQLITE_HEADER in data:
        problems.append("contains a SQLite database")
    if len(data) > MAX_BYTES:
        problems.append(f"is larger than {MAX_BYTES // 1024} KB")

    in_seed = path.is_relative_to(SEED_DIR)
    in_fixtures = path.is_relative_to(FIXTURE_DIR)
    if (
        lowered.suffix in STRUCTURED_SUFFIXES
        and not (in_seed or in_fixtures)
        and name not in ALLOWED_CONFIG
    ):
        problems.append(
            f"is a {lowered.suffix} file outside seed/ and tests/fixtures/"
        )
    if in_seed and path.suffix != ".json":
        problems.append("is not a .json file (seed/ holds the exercise library only)")

    if lowered.is_relative_to(FIXTURE_DIR) and not _is_synthetic(lowered.suffix, data):
        problems.append(
            'is a fixture without "synthetic": true or a first line "# SYNTHETIC"'
        )

    return problems


def _git(*args: str) -> bytes:
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def _names(output: bytes) -> list[str]:
    return [n for n in output.decode().split("\0") if n]


Item = tuple[str, str, Callable[[], bytes]]  # label, repo-relative name, reader


def staged_items() -> Iterator[Item]:
    for name in _names(_git("diff", "--cached", "--name-only", "-z", DIFF_FILTER)):
        yield name, name, lambda n=name: _git("show", f":{n}")


def commit_items(base: str, head: str) -> Iterator[Item]:
    """Files each commit in base..head touched, so a file that is added and
    then removed inside the range is still checked."""
    revs = _git("rev-list", f"{base}..{head}" if base else head).decode().split()
    for sha in revs:
        parents = _git("rev-list", "--parents", "-n", "1", sha).decode().split()[1:]
        against = parents[0] if parents else EMPTY_TREE
        names = _names(_git("diff", "--name-only", "-z", DIFF_FILTER, against, sha))
        for name in names:
            yield f"{sha[:9]}:{name}", name, lambda s=sha, n=name: _git("show", f"{s}:{n}")


def file_items(files: list[str]) -> Iterator[Item]:
    for name in files:
        yield name, name, lambda n=name: Path(n).read_bytes()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--commits", nargs=2, metavar=("BASE", "HEAD"))
    parser.add_argument("files", nargs="*")
    args = parser.parse_args(argv)

    if args.staged:
        items = list(staged_items())
    elif args.commits:
        items = list(commit_items(*args.commits))
    elif args.files:
        items = list(file_items(args.files))
    else:
        parser.error("give --staged, --commits BASE HEAD, or file names")

    failed = False
    for label, name, read in items:
        # Names only: never print file contents (§13.2).
        for problem in check_file(name, read()):
            print(f"check_private: {label} {problem}", file=sys.stderr)
            failed = True
    if failed:
        print(
            "check_private: blocked. Personal training information must never "
            "reach GitHub (DESIGN §13.2).",
            file=sys.stderr,
        )
        return 1
    print(f"check_private: {len(items)} file(s) ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
