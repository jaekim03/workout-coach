import subprocess

import pytest

from scripts import check_private
from scripts.check_private import check_file

OK = b"print('hello')\n"


@pytest.mark.parametrize(
    "name",
    [
        "src/coach/engine/load.py",
        "DESIGN.md",
        "seed/exercises.json",
        ".github/workflows/ci.yml",
        ".pre-commit-config.yaml",
        ".claude/settings.json",
        "pyproject.toml",
        "src/coach/migrations/0001_initial.sql",
    ],
)
def test_allowed_paths(name):
    assert check_file(name, OK) == []


@pytest.mark.parametrize(
    "name",
    [
        "coach.db",
        "backup/coach.sqlite",
        "x.sqlite3",
        "coach.db-wal",
        "coach.db-shm",
        "coach.db-journal",
        "history.csv",
        "seed/exercises.csv",
        "log.xlsx",
        "debug.log",
        ".env",
        ".env.local",
        "data/anything.txt",
        "src/exports/plan.md",
        "logs/run.txt",
        "transcripts/call.md",
        "screenshots/session.txt",
        # case variants
        "COACH.DB", "History.CSV", ".ENV", ".Env.local", "Data/real.txt",
        "EXPORTS/plan.md", "summary.JSON", "profile.YAML",
        # stricter than the spec (D-37)
        "dump.sql", "src/coach/migrations/dump.sql", "src/coach/migrations/0001_Initial.SQL",
        "migrations/0001_initial.sql", "src/coach/migrations/sub/0001_initial.sql",
        "history.tsv", "sets.jsonl", "coach.db.gz", "coach.db.bak",
        "backup.zip", "log.xls", "a.parquet", "a.pkl", "a.ipynb", "session.png",
        "x.log.1", "history.csv.txt", "prod.env", ".envrc",
        "seed/dump.txt", "seed/notes.md",
        # not normalized
        "seed/../summary.txt", "/abs/tests/fixtures/real.txt", "./README.md",
    ],
)
def test_blocked_patterns(name):
    assert check_file(name, OK)


def test_sqlite_header_is_caught_under_any_name():
    assert check_file("notes.txt", b"SQLite format 3\x00" + b"\x00" * 100)
    assert check_file("notes.txt", b"x" + b"SQLite format 3\x00")


def test_size_limit():
    assert check_file("big.md", b"a" * (500 * 1024)) == []
    assert check_file("big.md", b"a" * (500 * 1024 + 1))


@pytest.mark.parametrize(
    "name",
    [
        "summary.json",
        "src/coach/profile.yaml",
        "docs/plan.yml",
        ".github/workflows/other.yml",
        ".claude/settings.local.json",
    ],
)
def test_structured_files_outside_seed_and_fixtures(name):
    assert check_file(name, b"{}")


@pytest.mark.parametrize(
    "name, data",
    [
        ("tests/fixtures/block.json", b'{"synthetic": true, "sets": []}'),
        ("tests/fixtures/block.yaml", b"synthetic: true\nsets: []\n"),
        ("tests/fixtures/block.yml", b"# SYNTHETIC\nsets: []\n"),
        ("tests/fixtures/notes.txt", b"# SYNTHETIC\nfelt fine\n"),
    ],
)
def test_marked_fixtures_pass(name, data):
    assert check_file(name, data) == []


@pytest.mark.parametrize(
    "name, data",
    [
        ("tests/fixtures/block.json", b'{"sets": []}'),
        ("tests/fixtures/block.json", b'{"synthetic": false}'),
        ("tests/fixtures/block.json", b'{"synthetic": "true"}'),
        ("tests/fixtures/block.json", b'{"nested": {"synthetic": true}}'),
        ("tests/fixtures/block.json", b"not json"),
        ("tests/fixtures/block.yaml", b"sets: []\n"),
        ("tests/fixtures/block.yaml", b"meta:\n  synthetic: true\n"),
        ("tests/fixtures/notes.txt", b"felt fine\n# SYNTHETIC\n"),
        ("tests/fixtures/empty.txt", b""),
        ("tests/fixtures/block.JSON", b"# SYNTHETIC\n{}"),
        ("Tests/Fixtures/block.txt", b"real\n"),
    ],
)
def test_unmarked_fixtures_fail(name, data):
    assert check_file(name, data)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    git("config", "user.email", "synthetic@example.invalid")
    git("config", "user.name", "Synthetic")
    (tmp_path / "README.md").write_text("hi\n")
    git("add", "-A")
    git("commit", "-q", "-m", "init")
    monkeypatch.chdir(tmp_path)
    return tmp_path, git


def test_staged_mode_reads_the_index(repo, capsys):
    path, git = repo
    (path / "ok.py").write_text("x = 1\n")
    git("add", "ok.py")
    assert check_private.main(["--staged"]) == 0

    (path / "dump.txt").write_bytes(b"SQLite format 3\x00ZZPAYLOAD")
    git("add", "dump.txt")
    assert check_private.main(["--staged"]) == 1
    err = capsys.readouterr().err
    assert "dump.txt contains a SQLite database" in err
    assert "ZZPAYLOAD" not in err


def test_commits_mode_checks_every_commit(repo, capsys):
    path, git = repo
    (path / "summary.json").write_text("{}")
    git("add", "-f", "summary.json")
    git("commit", "-q", "-m", "bad")
    git("rm", "-q", "summary.json")
    git("commit", "-q", "-m", "remove")
    (path / "ok.py").write_text("x = 1\n")
    git("add", "ok.py")
    git("commit", "-q", "-m", "ok")

    # Added then removed inside the range: the net diff is clean, history is not.
    assert check_private.main(["--commits", "HEAD~3", "HEAD"]) == 1
    assert ":summary.json is a .json file" in capsys.readouterr().err
    assert check_private.main(["--commits", "HEAD~1", "HEAD"]) == 0
    # Empty base: all history, including the root commit.
    assert check_private.main(["--commits", "", "HEAD"]) == 1


def test_type_change_is_checked(repo):
    path, git = repo
    (path / "notes.txt").symlink_to("README.md")
    git("add", "notes.txt")
    git("commit", "-q", "-m", "link")
    (path / "notes.txt").unlink()
    (path / "notes.txt").write_bytes(b"SQLite format 3\x00")
    git("add", "notes.txt")
    assert check_private.main(["--staged"]) == 1


def test_no_mode_is_an_error():
    with pytest.raises(SystemExit) as exit_info:
        check_private.main([])
    assert exit_info.value.code == 2


def test_migrations_may_not_carry_literal_rows():
    name = "src/coach/migrations/0002_change.sql"
    assert check_file(name, b"ALTER TABLE a ADD COLUMN y INTEGER;\nINSERT INTO b SELECT * FROM a;\n") == []
    assert check_file(name, b"INSERT INTO set_entry (id) VALUES (1);\n")
    assert check_file(name, b"insert into profile values (1, 'x');\n")
