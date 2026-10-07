import copy
import json

import pytest

from coach import db
from coach.seed import SeedError, load_seed, validate

SEED = {
    "equipment": [
        {"name": "barbell", "increment_kg": 2.5},
        {"name": "pullup_bar", "increment_kg": None},
    ],
    "exercises": [
        {
            "name": "Synthetic Press",
            "movement_pattern": "h_push",
            "equipment": "barbell",
            "load_type": "external",
            "unilateral": False,
            "stretch_bias": False,
            "aliases": ["synth press"],
            "muscles": {"chest": 1.0, "triceps": 0.5},
        },
        {
            "name": "Synthetic Hang",
            "movement_pattern": "v_pull",
            "equipment": "pullup_bar",
            "load_type": "bodyweight",
            "unilateral": False,
            "stretch_bias": True,
            "aliases": [],
            "muscles": {"back": 1.0},
        },
    ],
}


@pytest.fixture
def conn():
    connection = db.connect(":memory:")
    db.migrate(connection)
    return connection


def write(tmp_path, seed):
    path = tmp_path / "exercises.json"
    path.write_text(json.dumps(seed))
    return path


def test_load_inserts_every_table(conn, tmp_path):
    assert load_seed(conn, write(tmp_path, SEED)) == 2
    row = conn.execute(
        "SELECT e.movement_pattern, q.name FROM exercise e"
        " JOIN exercise_alias a ON a.exercise_id = e.id"
        " JOIN equipment q ON q.id = e.equipment_id WHERE a.alias = 'SYNTH PRESS'"
    ).fetchone()
    assert tuple(row) == ("h_push", "barbell")
    muscles = conn.execute(
        "SELECT muscle, weight FROM exercise_muscle m JOIN exercise e ON e.id = m.exercise_id"
        " WHERE e.name = 'Synthetic Press' ORDER BY muscle"
    ).fetchall()
    assert [tuple(m) for m in muscles] == [("chest", 1.0), ("triceps", 0.5)]


def test_reload_updates_library_but_keeps_user_equipment(conn, tmp_path):
    load_seed(conn, write(tmp_path, SEED))
    conn.execute("UPDATE equipment SET increment_kg = 1.25, available = 0 WHERE name = 'barbell'")

    changed = copy.deepcopy(SEED)
    changed["exercises"][0]["muscles"] = {"chest": 1.0}
    changed["exercises"][0]["aliases"] = ["sp"]
    load_seed(conn, write(tmp_path, changed))

    assert conn.execute("SELECT COUNT(*) FROM exercise").fetchone()[0] == 2
    assert conn.execute("SELECT COUNT(*) FROM exercise_muscle").fetchone()[0] == 2
    assert [r[0] for r in conn.execute("SELECT alias FROM exercise_alias")] == ["sp"]
    assert tuple(conn.execute(
        "SELECT increment_kg, available FROM equipment WHERE name = 'barbell'"
    ).fetchone()) == (1.25, 0)


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda s: s["exercises"][0].update(muscles={}), "at least one muscle"),
        (lambda s: s["exercises"][0].update(equipment="kettlebell"), "unknown equipment"),
        (lambda s: s["exercises"][1].update(name="synthetic press"), "duplicate exercise"),
        (lambda s: s["exercises"][1].update(aliases=["Synth Press"]), "is used by"),
        (lambda s: s["exercises"][1].update(aliases=["synthetic press"]), "another exercise's name"),
    ],
)
def test_validate_rejects(change, message):
    seed = copy.deepcopy(SEED)
    change(seed)
    with pytest.raises(SeedError, match=message):
        validate(seed)


def test_schema_rejects_bad_weights(conn, tmp_path):
    seed = copy.deepcopy(SEED)
    seed["exercises"][0]["muscles"] = {"chest": 0.7}
    with pytest.raises(Exception):
        load_seed(conn, write(tmp_path, seed))
    assert conn.execute("SELECT COUNT(*) FROM exercise").fetchone()[0] == 0


def names(conn):
    return {r[0] for r in conn.execute("SELECT name FROM exercise")}


def test_reload_handles_renames_and_moved_aliases(conn, tmp_path):
    load_seed(conn, write(tmp_path, SEED))
    changed = copy.deepcopy(SEED)
    changed["exercises"][0]["name"] = "Synthetic Bench"          # rename, alias kept
    changed["exercises"][1]["name"] = "synthetic hang"           # case-only rename
    changed["exercises"][1]["aliases"] = ["hang"]
    load_seed(conn, write(tmp_path, changed))
    assert names(conn) == {"Synthetic Bench", "synthetic hang"}

    moved = copy.deepcopy(changed)
    moved["exercises"][0]["aliases"] = ["hang"]                 # alias moves to an earlier exercise
    moved["exercises"][1]["aliases"] = ["synth press"]
    load_seed(conn, write(tmp_path, moved))
    owner = conn.execute(
        "SELECT e.name FROM exercise e JOIN exercise_alias a ON a.exercise_id = e.id WHERE a.alias = 'hang'"
    ).fetchone()[0]
    assert owner == "Synthetic Bench"


def test_removed_exercise_is_kept_only_if_logged_data_uses_it(conn, tmp_path):
    load_seed(conn, write(tmp_path, SEED))
    press_id = conn.execute("SELECT id FROM exercise WHERE name = 'Synthetic Press'").fetchone()[0]
    conn.execute(
        "INSERT INTO baseline (exercise_id, weight_kg, reps, reported_at) VALUES (?, 40, 8, 'x')",
        (press_id,),
    )
    conn.commit()

    emptied = copy.deepcopy(SEED)
    emptied["exercises"] = []
    load_seed(conn, write(tmp_path, emptied))
    assert names(conn) == {"Synthetic Press"}
    assert conn.execute("SELECT COUNT(*) FROM exercise_alias").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM exercise_muscle").fetchone()[0] == 2
