"""SQLite access: data directory, connection and migrations (DESIGN §3, §4)."""
from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

DATA_DIR_ENV = "COACH_DATA_DIR"
DEFAULT_DATA_DIR = "~/.workout-coach"
DB_NAME = "coach.db"
MIGRATIONS_DIR = Path(__file__).parent / "migrations"
MIGRATION_NAME = re.compile(r"(\d{4})_[a-z0-9_]+\.sql")
# The runner owns the transaction; a script that ends it would half-apply.
TRANSACTION_CONTROL = re.compile(
    r"^\s*(COMMIT|ROLLBACK|END[ \t]+TRANSACTION"
    r"|BEGIN([ \t]+(TRANSACTION|DEFERRED|IMMEDIATE|EXCLUSIVE))*[ \t]*;)",
    re.IGNORECASE | re.MULTILINE,
)
PRIVATE_DIR = 0o700
PRIVATE_FILE = 0o600


class DataDirError(RuntimeError):
    pass


class MigrationError(RuntimeError):
    pass


def data_dir() -> Path:
    """The personal data directory. Never inside a git work tree (D-6)."""
    path = Path(os.environ.get(DATA_DIR_ENV) or DEFAULT_DATA_DIR).expanduser().resolve()
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            raise DataDirError(
                f"data directory {path} is inside the git work tree {candidate}; "
                f"set {DATA_DIR_ENV} to a directory outside any repository"
            )
    return path


def connect(path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrations(directory: Path = MIGRATIONS_DIR) -> list[tuple[int, Path]]:
    """(version, file) in order. Versions must run 1..n with no gaps."""
    found = []
    for file in sorted(directory.glob("*.sql")):
        match = MIGRATION_NAME.fullmatch(file.name)
        if not match:
            raise MigrationError(f"bad migration file name: {file.name}")
        found.append((int(match.group(1)), file))
    versions = [version for version, _ in found]
    if versions != list(range(1, len(found) + 1)):
        raise MigrationError(f"migration versions must be 1..n without gaps: {versions}")
    return found


def schema_version(conn: sqlite3.Connection) -> int:
    return conn.execute("PRAGMA user_version").fetchone()[0]


def migrate(
    conn: sqlite3.Connection,
    directory: Path = MIGRATIONS_DIR,
    backup_dir: Path | None = None,
) -> int:
    """Apply pending migrations in order and return the schema version.

    Forward-only. Each migration runs in its own transaction. If `backup_dir`
    is given, an existing database is copied there before anything is applied.

    Foreign keys are off while a script runs, so it can rebuild a table that
    others reference; `foreign_key_check` must come back clean before commit.
    """
    if conn.in_transaction:
        raise MigrationError("migrate() needs a connection with no open transaction")
    available = migrations(directory)
    latest = available[-1][0] if available else 0
    current = schema_version(conn)
    if current > latest:
        raise MigrationError(
            f"database is at schema version {current}, but this code only knows "
            f"up to {latest}; update the app"
        )
    pending = [(version, file) for version, file in available if version > current]
    if pending and current and backup_dir is not None:
        backup_path = backup_dir / f"{DB_NAME}.v{current}.bak"
        backup_path.touch(mode=PRIVATE_FILE)
        backup = sqlite3.connect(backup_path)
        with backup:
            conn.backup(backup)
        backup.close()

    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        for version, file in pending:
            _apply(conn, version, file)
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
    return schema_version(conn)


def _apply(conn: sqlite3.Connection, version: int, file: Path) -> None:
    script = file.read_text()
    if TRANSACTION_CONTROL.search(script):
        raise MigrationError(f"{file.name} must not contain BEGIN, COMMIT or ROLLBACK")
    if not sqlite3.complete_statement(script):
        raise MigrationError(f"{file.name} does not end with a complete statement")
    try:
        conn.executescript(f"BEGIN;\n{script}")
        if not conn.in_transaction:
            raise MigrationError(f"{file.name} ended the migration transaction")
        broken = conn.execute("PRAGMA foreign_key_check").fetchall()
        if broken:
            raise MigrationError(
                f"{file.name} leaves {len(broken)} broken foreign key reference(s)"
            )
        conn.execute(f"PRAGMA user_version = {version}")
        conn.execute("COMMIT")
    except (sqlite3.Error, MigrationError) as error:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        if isinstance(error, MigrationError):
            raise
        raise MigrationError(f"{file.name} failed: {error}") from error


def open_db() -> sqlite3.Connection:
    """Open the user's database: create, migrate and load the exercise library.

    The directory and the database are readable by the owner only.
    """
    from coach.seed import load_seed

    directory = data_dir()
    directory.mkdir(mode=PRIVATE_DIR, parents=True, exist_ok=True)
    directory.chmod(PRIVATE_DIR)
    path = directory / DB_NAME
    path.touch(mode=PRIVATE_FILE)
    path.chmod(PRIVATE_FILE)
    conn = connect(path)
    migrate(conn, backup_dir=directory)
    load_seed(conn)
    return conn
