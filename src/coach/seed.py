"""Load the generic exercise library (DESIGN §4) into the database."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

# Installed wheels carry the file inside the package (pyproject force-include);
# a source checkout reads it from seed/.
_PACKAGED = Path(__file__).resolve().parent / "exercises.json"
SEED_FILE = _PACKAGED if _PACKAGED.exists() else Path(__file__).resolve().parents[2] / "seed" / "exercises.json"
# Tables whose rows keep an exercise alive after it leaves the seed.
REFERENCING = (
    ("block_slot", "exercise_id"),
    ("set_entry", "exercise_id"),
    ("baseline", "exercise_id"),
    ("limitation", "excluded_exercise_id"),
)


class SeedError(ValueError):
    pass


def validate(seed: dict) -> None:
    """Checks the schema cannot express. The schema's own CHECKs cover the rest."""
    equipment = {item["name"] for item in seed["equipment"]}
    names: set[str] = set()
    aliases: dict[str, str] = {}
    for exercise in seed["exercises"]:
        name = exercise["name"]
        if name.lower() in names:
            raise SeedError(f"duplicate exercise: {name}")
        names.add(name.lower())
        if not exercise["muscles"]:
            raise SeedError(f"{name}: needs at least one muscle")
        if exercise["equipment"] is not None and exercise["equipment"] not in equipment:
            raise SeedError(f"{name}: unknown equipment {exercise['equipment']}")
        for alias in exercise["aliases"]:
            owner = aliases.setdefault(alias.lower(), name)
            if owner != name:
                raise SeedError(f"alias {alias!r} is used by {owner} and {name}")
    for alias, owner in aliases.items():
        if alias in names and alias != owner.lower():
            raise SeedError(f"alias {alias!r} of {owner} is another exercise's name")


def load_seed(conn: sqlite3.Connection, path: Path = SEED_FILE) -> int:
    """Insert or update the library and return the number of exercises (D-59).

    Safe to run again after the seed file changes. Exercises are matched by
    exact name. Aliases and muscle maps are replaced from the file. An exercise
    no longer in the file is deleted unless logged data refers to it. Existing
    equipment rows are left alone: their availability and increments belong to
    the user.
    """
    seed = json.loads(path.read_text())
    validate(seed)
    with conn:
        for item in seed["equipment"]:
            conn.execute(
                "INSERT INTO equipment (name, increment_kg) VALUES (?, ?) "
                "ON CONFLICT (name) DO NOTHING",
                (item["name"], item["increment_kg"]),
            )
        equipment_ids = dict(conn.execute("SELECT name, id FROM equipment").fetchall())

        # Aliases are seed-owned; clearing them first lets one move between exercises.
        conn.execute("DELETE FROM exercise_alias")
        seeded = {exercise["name"] for exercise in seed["exercises"]}
        for exercise_id, name in conn.execute("SELECT id, name FROM exercise").fetchall():
            if name in seeded or any(
                conn.execute(f"SELECT 1 FROM {table} WHERE {column} = ? LIMIT 1", (exercise_id,)).fetchone()
                for table, column in REFERENCING
            ):
                continue
            conn.execute("DELETE FROM exercise_muscle WHERE exercise_id = ?", (exercise_id,))
            conn.execute("DELETE FROM exercise WHERE id = ?", (exercise_id,))

        for exercise in seed["exercises"]:
            conn.execute(
                "INSERT INTO exercise (name, movement_pattern, equipment_id, load_type,"
                " unilateral, stretch_bias) VALUES (?, ?, ?, ?, ?, ?) "
                "ON CONFLICT (name) DO UPDATE SET"
                " movement_pattern = excluded.movement_pattern,"
                " equipment_id = excluded.equipment_id,"
                " load_type = excluded.load_type,"
                " unilateral = excluded.unilateral,"
                " stretch_bias = excluded.stretch_bias",
                (
                    exercise["name"],
                    exercise["movement_pattern"],
                    equipment_ids.get(exercise["equipment"]),
                    exercise["load_type"],
                    int(exercise["unilateral"]),
                    int(exercise["stretch_bias"]),
                ),
            )
            (exercise_id,) = conn.execute(
                "SELECT id FROM exercise WHERE name = ?", (exercise["name"],)
            ).fetchone()
            conn.execute("DELETE FROM exercise_muscle WHERE exercise_id = ?", (exercise_id,))
            conn.executemany(
                "INSERT INTO exercise_muscle (exercise_id, muscle, weight) VALUES (?, ?, ?)",
                [(exercise_id, muscle, weight) for muscle, weight in exercise["muscles"].items()],
            )
            conn.executemany(
                "INSERT INTO exercise_alias (alias, exercise_id) VALUES (?, ?)",
                [(alias, exercise_id) for alias in exercise["aliases"]],
            )
    return len(seed["exercises"])
