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


# --- the real library (seed/exercises.json) ---

from coach.seed import SEED_FILE

LIBRARY = json.loads(SEED_FILE.read_text())
PATTERNS = {"squat", "hinge", "h_push", "v_push", "h_pull", "v_pull", "lunge", "core", "isolation"}
MUSCLES = {
    "chest", "back", "quads", "hamstrings", "glutes", "side_delts",
    "rear_delts", "front_delts", "biceps", "triceps", "calves", "abs",
}
# Equipment a commercial gym without free barbells or racks still offers.
NO_BARBELL_GYM = {"dumbbell", "cable", "machine", "smith_machine", "plate_loaded", "fixed_barbell", None}


def test_library_loads(conn):
    count = load_seed(conn)
    assert count == len(LIBRARY["exercises"]) >= 40
    without_muscles = conn.execute(
        "SELECT COUNT(*) FROM exercise e WHERE NOT EXISTS"
        " (SELECT 1 FROM exercise_muscle m WHERE m.exercise_id = e.id)"
    ).fetchone()[0]
    assert without_muscles == 0


def test_library_covers_every_pattern_and_muscle():
    exercises = LIBRARY["exercises"]
    assert {e["movement_pattern"] for e in exercises} == PATTERNS
    primary = {m for e in exercises for m, w in e["muscles"].items() if w == 1.0}
    assert primary == MUSCLES


def test_library_works_without_a_free_barbell():
    usable = [e for e in LIBRARY["exercises"] if e["equipment"] in NO_BARBELL_GYM]
    assert {e["movement_pattern"] for e in usable} == PATTERNS
    primary = {m for e in usable for m, w in e["muscles"].items() if w == 1.0}
    assert primary == MUSCLES


def test_library_follows_the_design_muscle_map():
    expected = {
        "squat": [{"quads": 1.0, "glutes": 1.0}, {"quads": 1.0, "glutes": 0.5}],
        "lunge": [{"quads": 1.0, "glutes": 1.0}],
        "hinge": [{"hamstrings": 1.0, "glutes": 0.5}, {"glutes": 1.0}],
        "h_push": [{"chest": 1.0, "triceps": 0.5, "front_delts": 0.5}],
        "v_push": [{"front_delts": 1.0, "triceps": 0.5, "side_delts": 0.5}],
        "h_pull": [{"back": 1.0, "biceps": 0.5, "rear_delts": 0.5}],
        "v_pull": [{"back": 1.0, "biceps": 0.5, "rear_delts": 0.5}],
    }
    for exercise in LIBRARY["exercises"]:
        pattern = exercise["movement_pattern"]
        if pattern in expected:
            assert exercise["muscles"] in expected[pattern], exercise["name"]
        else:  # isolation and core train the target muscle only
            assert list(exercise["muscles"].values()) == [1.0], exercise["name"]


def test_library_has_the_gap_fillers():
    names = {e["name"] for e in LIBRARY["exercises"]}
    assert {
        "Seated Leg Curl", "Leg Extension", "Dumbbell Lateral Raise",
        "Overhead Cable Triceps Extension", "Standing Calf Raise",
    } <= names


def test_bodyweight_exercises_have_no_loaded_equipment():
    increments = {e["name"]: e["increment_kg"] for e in LIBRARY["equipment"]}
    for exercise in LIBRARY["exercises"]:
        if exercise["load_type"] == "bodyweight":
            assert increments.get(exercise["equipment"]) is None, exercise["name"]
        else:
            assert increments[exercise["equipment"]] is not None, exercise["name"]
