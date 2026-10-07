from pathlib import Path

import subprocess

from scripts.check_decisions import (
    changed_migrations,
    config_constants,
    locked_changes,
    numeric_literals,
    parse_decisions,
    run,
)

REPO = Path(__file__).resolve().parent.parent


def entry(n, status="locked", kind="one-way", choice="A", answered=None):
    text = (
        f"## D-{n}: Question {n}?\n"
        f"Status: {status}\nType: {kind}\nChoice: {choice}\nRationale: because\n"
    )
    if answered:
        text += f"Answered: {answered}\n"
    return text


def parsed(text):
    return parse_decisions(text)[0]


def test_parse_reads_fields():
    entries, errors = parse_decisions("# Decisions\n\n" + entry(1) + "\n" + entry(2, "open", "two-way"))
    assert errors == []
    assert entries["D-1"].fields["Status"] == "locked"
    assert entries["D-2"].fields["Type"] == "two-way"


def test_parse_reports_bad_entries():
    text = "## D-1: Q?\nStatus: maybe\nType: one-way\nChoice: A\n" + entry(1)
    _, errors = parse_decisions(text)
    assert "D-1: missing field Rationale" in errors
    assert "D-1: Status must be locked or open" in errors
    assert "D-1: duplicate entry" in errors


def test_numeric_literals_exemptions():
    source = (
        "def f(xs, a):\n"
        "    '''Uses 30 reps.'''\n"
        "    first = xs[0] + xs[2] + xs[1:5][-3]\n"
        "    ok = a + 1 - 0 + True\n"
        "    return a * 30 + 0.9, -2\n"
    )
    assert numeric_literals(source) == [(5, 30), (5, 0.9), (5, 2)]


def test_config_constants_need_a_decision_comment():
    source = (
        "EPLEY = 30  # D-4\n"
        "# D-5, D-6\n"
        "STEPS = {\n"
        "    'lower': 0.05,\n"
        "}\n"
        "CAP: float = 1.10\n"
        "_private = 3\n"
        "helper = 2\n"
    )
    assert config_constants(source) == [
        ("EPLEY", 1, {"D-4"}),
        ("STEPS", 3, {"D-5", "D-6"}),
        ("CAP", 6, set()),
    ]


A1 = "2030-01-01 via /decisions"
A2 = "2030-02-01 via /decisions"


def test_unchanged_locked_entries_pass():
    base = parsed(entry(1) + entry(2, answered=A1))
    assert locked_changes(base, parsed(entry(1) + entry(2, answered=A1))) == []


def test_locked_one_way_change_needs_new_answer():
    base = parsed(entry(1) + entry(2, answered=A1))
    assert len(locked_changes(base, parsed(entry(1, choice="B") + entry(2, choice="B", answered=A1)))) == 2
    assert locked_changes(base, parsed(entry(1, choice="B", answered=A2) + entry(2, choice="B", answered=A2))) == []
    assert locked_changes(base, parsed(entry(1) + entry(2, choice="B", answered=A1 + " (2)"))) == []


def test_answer_format_is_checked():
    base = parsed(entry(1))
    assert locked_changes(base, parsed(entry(1, choice="B", answered="x")))
    assert locked_changes(base, parsed(entry(1, choice="B", answered="yesterday via /decisions")))


def test_removing_or_reopening_a_locked_entry_fails():
    base = parsed(entry(1) + entry(2))
    assert len(locked_changes(base, parsed(entry(2)))) == 1
    assert len(locked_changes(base, parsed(entry(1, status="open") + entry(2, kind="two-way")))) == 2


def test_becoming_locked_needs_an_answer():
    base = parsed(entry(1, status="open"))
    assert locked_changes(base, parsed(entry(1)))
    assert locked_changes(base, parsed(entry(1, answered=A1))) == []
    # a brand-new entry added as locked
    assert locked_changes(base, parsed(entry(1, status="open") + entry(2)))
    assert locked_changes(base, parsed(entry(1, status="open") + entry(2, answered=A1))) == []


def test_two_way_and_open_entries_may_change():
    base = parsed(entry(1, kind="two-way") + entry(2, status="open"))
    head = parsed(entry(1, kind="two-way", choice="B") + entry(2, status="open", choice="B"))
    assert locked_changes(base, head) == []


def test_parse_reports_malformed_headings_and_duplicate_fields():
    _, errors = parse_decisions("## D-3 - no colon\n" + entry(1) + "Status: open\n")
    assert any("malformed entry heading" in e for e in errors)
    assert "D-1: a field appears more than once" in errors


def make_repo(tmp_path, engine_source, config_source):
    (tmp_path / "DECISIONS.md").write_text(entry(1, kind="two-way"))
    engine = tmp_path / "src/coach/engine"
    engine.mkdir(parents=True)
    (engine / "load.py").write_text(engine_source)
    (tmp_path / "src/coach/config.py").write_text(config_source)
    return tmp_path


def test_run_passes_on_a_clean_tree(tmp_path):
    root = make_repo(tmp_path, "from coach import config\nx = config.EPLEY + 1\n", "EPLEY = 30  # D-1\n")
    assert run(root, None) == []


def test_run_reports_literals_and_unknown_decisions(tmp_path):
    root = make_repo(tmp_path, "x = 30\n", "EPLEY = 30  # D-9\nCAP = 1.1\n")
    errors = run(root, None)
    assert any("load.py:1: numeric literal 30" in e for e in errors)
    assert any("EPLEY cites D-9" in e for e in errors)
    assert any("CAP has no # D-<n> comment" in e for e in errors)


def test_run_requires_decisions_file(tmp_path):
    assert run(tmp_path, None) == ["DECISIONS.md is missing"]


def test_this_repo_passes():
    assert run(REPO, None) == []


def test_merged_migrations_may_not_change(tmp_path):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    directory = tmp_path / "src/coach/migrations"
    directory.mkdir(parents=True)
    (directory / "0001_a.sql").write_text("CREATE TABLE a (x);\n")
    git("init", "-q", "-b", "main")
    git("config", "user.email", "synthetic@example.invalid")
    git("config", "user.name", "Synthetic")
    git("add", "-A")
    git("commit", "-q", "-m", "base")

    (directory / "0002_b.sql").write_text("CREATE TABLE b (x);\n")
    git("add", "-A")
    git("commit", "-q", "-m", "add")
    (directory / "0002_b.sql").write_text("CREATE TABLE b (y);\n")
    git("commit", "-q", "-am", "edit a migration that is new in this range")
    assert changed_migrations("main~2", tmp_path) == []

    (directory / "0001_a.sql").write_text("CREATE TABLE a (y);\n")
    git("commit", "-q", "-am", "edit merged")
    assert len(changed_migrations("main~3", tmp_path)) == 1

    git("mv", "src/coach/migrations/0001_a.sql", "src/coach/migrations/0001_z.sql")
    git("commit", "-q", "-m", "rename merged")
    assert any("0001_a.sql" in e for e in changed_migrations("main~4", tmp_path))

    (directory / "0001_z.sql").unlink()
    (directory / "0001_z.sql").symlink_to("0002_b.sql")
    git("commit", "-q", "-am", "type change")
    assert any("0001_z.sql" in e for e in changed_migrations("main~1", tmp_path))
