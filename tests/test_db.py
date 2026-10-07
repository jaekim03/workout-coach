import re
import sqlite3
from pathlib import Path

import pytest

from coach import db

REPO = Path(__file__).resolve().parent.parent
TABLES = {
    "profile", "equipment", "exercise", "exercise_muscle", "exercise_alias",
    "limitation", "baseline", "agent_call", "block", "block_slot", "session",
    "set_entry",
}


@pytest.fixture
def conn():
    connection = db.connect(":memory:")
    db.migrate(connection)
    yield connection
    connection.close()


def shape(connection):
    """Tables with their columns and foreign keys, for comparing two schemas."""
    tables = [r[0] for r in connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]
    return {
        table: (
            [tuple(r) for r in connection.execute(f"PRAGMA table_info({table})")],
            sorted(tuple(r)[2:5] for r in connection.execute(f"PRAGMA foreign_key_list({table})")),
        )
        for table in tables
    }


def test_migrations_build_the_design_schema(conn):
    design = (REPO / "DESIGN.md").read_text()
    reference = sqlite3.connect(":memory:")
    reference.executescript(re.search(r"```sql\n(.*?)```", design, re.S).group(1))

    assert set(shape(conn)) == TABLES
    assert shape(conn) == shape(reference)
    assert db.schema_version(conn) == len(db.migrations())


def test_migrate_is_idempotent(conn):
    assert db.migrate(conn) == db.schema_version(conn)


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO profile (id, goal, training_age_months, days_per_week, session_minutes, updated_at)"
        " VALUES (2, 'hypertrophy', 12, 4, 60, 'x')",
        "INSERT INTO profile (id, goal, training_age_months, days_per_week, session_minutes, updated_at)"
        " VALUES (1, 'hypertrophy', 12, 7, 60, 'x')",
        "INSERT INTO exercise (name, movement_pattern, load_type) VALUES ('x', 'push', 'external')",
        "INSERT INTO exercise_muscle (exercise_id, muscle, weight) VALUES (1, 'chest', 0.7)",
        "INSERT INTO exercise_muscle (exercise_id, muscle, weight) VALUES (1, 'forearms', 1.0)",
        "INSERT INTO exercise_muscle (exercise_id, muscle, weight) VALUES (99, 'chest', 1.0)",
    ],
)
def test_constraints_reject_bad_rows(conn, sql):
    conn.execute(
        "INSERT INTO exercise (id, name, movement_pattern, load_type) VALUES (1, 'a', 'h_push', 'external')"
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(sql)


def write_migrations(directory, *scripts):
    directory.mkdir(exist_ok=True)
    for number, script in enumerate(scripts, start=1):
        (directory / f"{number:04d}_step.sql").write_text(script)
    return directory


def test_pending_migrations_apply_in_order_with_backup(tmp_path):
    migrations = write_migrations(tmp_path / "m", "CREATE TABLE a (x INTEGER);")
    connection = db.connect(tmp_path / db.DB_NAME)
    assert db.migrate(connection, migrations, backup_dir=tmp_path) == 1
    assert not list(tmp_path.glob("*.bak"))  # nothing to back up on first creation
    connection.execute("INSERT INTO a VALUES (7)")
    connection.commit()

    write_migrations(migrations, "CREATE TABLE a (x INTEGER);", "ALTER TABLE a ADD COLUMN y INTEGER;")
    assert db.migrate(connection, migrations, backup_dir=tmp_path) == 2
    assert tuple(connection.execute("SELECT x, y FROM a").fetchone()) == (7, None)

    backup = sqlite3.connect(tmp_path / f"{db.DB_NAME}.v1.bak")
    assert backup.execute("PRAGMA user_version").fetchone()[0] == 1
    assert backup.execute("SELECT x FROM a").fetchone()[0] == 7


def test_failed_migration_rolls_back(tmp_path):
    migrations = write_migrations(
        tmp_path / "m",
        "CREATE TABLE a (x INTEGER);",
        "CREATE TABLE b (x INTEGER); INSERT INTO missing VALUES (1);",
    )
    connection = db.connect(":memory:")
    with pytest.raises(db.MigrationError, match="0002_step.sql failed"):
        db.migrate(connection, migrations)
    assert db.schema_version(connection) == 1
    tables = {r[0] for r in connection.execute("SELECT name FROM sqlite_master")}
    assert tables == {"a"}


def test_newer_database_is_refused(conn):
    conn.execute("PRAGMA user_version = 999")
    with pytest.raises(db.MigrationError, match="update the app"):
        db.migrate(conn)


def test_migration_numbering_is_checked(tmp_path):
    directory = tmp_path / "m"
    directory.mkdir()
    (directory / "0002_late.sql").write_text("SELECT 1;")
    with pytest.raises(db.MigrationError, match="without gaps"):
        db.migrations(directory)
    (directory / "first.sql").write_text("SELECT 1;")
    with pytest.raises(db.MigrationError, match="bad migration file name"):
        db.migrations(directory)


def test_data_dir_default_and_override(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv(db.DATA_DIR_ENV, raising=False)
    assert db.data_dir() == (tmp_path / ".workout-coach").resolve()
    monkeypatch.setenv(db.DATA_DIR_ENV, str(tmp_path / "elsewhere"))
    assert db.data_dir() == (tmp_path / "elsewhere").resolve()


def test_data_dir_inside_a_git_work_tree_is_refused(tmp_path, monkeypatch):
    (tmp_path / "repo" / ".git").mkdir(parents=True)
    monkeypatch.setenv(db.DATA_DIR_ENV, str(tmp_path / "repo" / "nested" / "store"))
    with pytest.raises(db.DataDirError, match="inside the git work tree"):
        db.data_dir()
    monkeypatch.setenv(db.DATA_DIR_ENV, str(REPO / "store"))
    with pytest.raises(db.DataDirError):
        db.data_dir()


def test_open_db_creates_a_private_directory(tmp_path, monkeypatch):
    monkeypatch.setenv(db.DATA_DIR_ENV, str(tmp_path / "store"))
    connection = db.open_db()
    assert db.schema_version(connection) == len(db.migrations())
    assert (tmp_path / "store" / db.DB_NAME).exists()
    assert (tmp_path / "store").stat().st_mode & 0o777 == 0o700
    assert (tmp_path / "store" / db.DB_NAME).stat().st_mode & 0o777 == 0o600


def test_open_db_tightens_an_existing_directory(tmp_path, monkeypatch):
    (tmp_path / "store").mkdir(mode=0o755)
    monkeypatch.setenv(db.DATA_DIR_ENV, str(tmp_path / "store"))
    db.open_db().close()
    assert (tmp_path / "store").stat().st_mode & 0o777 == 0o700


def test_migration_can_rebuild_a_referenced_table(tmp_path):
    migrations = write_migrations(
        tmp_path / "m",
        "CREATE TABLE parent (id INTEGER PRIMARY KEY, kind TEXT CHECK (kind IN ('a')));"
        "CREATE TABLE child (parent_id INTEGER NOT NULL REFERENCES parent(id));",
    )
    connection = db.connect(":memory:")
    db.migrate(connection, migrations)
    connection.execute("INSERT INTO parent VALUES (1, 'a')")
    connection.execute("INSERT INTO child VALUES (1)")
    connection.commit()

    rebuild = (
        "CREATE TABLE parent_new (id INTEGER PRIMARY KEY, kind TEXT CHECK (kind IN ('a', 'b')));"
        "INSERT INTO parent_new SELECT * FROM parent;"
        "DROP TABLE parent;"
        "ALTER TABLE parent_new RENAME TO parent;"
    )
    (migrations / "0002_step.sql").write_text(rebuild)
    assert db.migrate(connection, migrations) == 2
    connection.execute("INSERT INTO parent VALUES (2, 'b')")
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_migration_leaving_broken_references_rolls_back(tmp_path):
    migrations = write_migrations(
        tmp_path / "m",
        "CREATE TABLE parent (id INTEGER PRIMARY KEY);"
        "CREATE TABLE child (parent_id INTEGER NOT NULL REFERENCES parent(id));",
    )
    connection = db.connect(":memory:")
    db.migrate(connection, migrations)
    connection.execute("INSERT INTO parent VALUES (1)")
    connection.execute("INSERT INTO child VALUES (1)")
    connection.commit()
    (migrations / "0002_step.sql").write_text("DELETE FROM parent;")
    with pytest.raises(db.MigrationError, match="broken foreign key"):
        db.migrate(connection, migrations)
    assert db.schema_version(connection) == 1
    assert connection.execute("SELECT COUNT(*) FROM parent").fetchone()[0] == 1


@pytest.mark.parametrize(
    "script, message",
    [
        ("CREATE TABLE a (x); COMMIT; CREATE TABLE b (x);", "ended the migration transaction"),
        ("CREATE TABLE a (x);\nCOMMIT;\nCREATE TABLE b (x);", "must not contain"),
        ("BEGIN;\nCREATE TABLE a (x);", "must not contain"),
        ("CREATE TABLE a (x);\nrollback;", "must not contain"),
        ("CREATE TABLE a (x); /* never closed", "complete statement"),
    ],
)
def test_migration_scripts_may_not_control_the_transaction(tmp_path, script, message):
    migrations = write_migrations(tmp_path / "m", script)
    connection = db.connect(":memory:")
    with pytest.raises(db.MigrationError, match=message):
        db.migrate(connection, migrations)
    assert db.schema_version(connection) == 0


def test_trigger_bodies_are_allowed(tmp_path):
    migrations = write_migrations(
        tmp_path / "m",
        "CREATE TABLE a (x INTEGER);\n"
        "CREATE TRIGGER t AFTER INSERT ON a\nBEGIN\n  DELETE FROM a;\nEND;\n",
    )
    assert db.migrate(db.connect(":memory:"), migrations) == 1


def test_migrate_refuses_an_open_transaction(conn):
    conn.execute("INSERT INTO equipment (name) VALUES ('synthetic')")
    with pytest.raises(db.MigrationError, match="no open transaction"):
        db.migrate(conn)
