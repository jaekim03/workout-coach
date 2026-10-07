"""Synthetic data generator (DESIGN §13.2).

Every value comes from a seeded random generator. Nothing here is imported,
sampled or transformed from a real database. Rows are plain dicts keyed by the
DESIGN §4 column names.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

DEFAULT_SEED = 20261005
START_DATE = date(2030, 1, 7)
GOALS = ("strength", "hypertrophy", "general")
MUSCLES = (
    "chest", "back", "quads", "hamstrings", "glutes", "side_delts",
    "rear_delts", "front_delts", "biceps", "triceps", "calves", "abs",
)
REP_RANGES = ((6, 10), (8, 12), (10, 15), (12, 20))
INCREMENTS_KG = (1.0, 2.0, 2.5, 5.0)


class Factory:
    def __init__(self, seed: int = DEFAULT_SEED) -> None:
        self.rng = random.Random(seed)
        self._next_id = 0

    def _id(self) -> int:
        self._next_id += 1
        return self._next_id

    def profile(self, **overrides) -> dict:
        rng = self.rng
        row = {
            "id": 1,
            "goal": rng.choice(GOALS),
            "training_age_months": rng.randint(0, 120),
            "days_per_week": rng.randint(2, 6),
            "session_minutes": rng.choice((45, 60, 75, 90)),
            "display_unit": rng.choice(("kg", "lb")),
            "priority_muscles": rng.sample(MUSCLES, rng.randint(0, 2)),
            "sex": None,
            "birth_year": None,
            "height_cm": None,
            "bodyweight_kg": None,
            "updated_at": START_DATE.isoformat(),
        }
        return row | overrides

    def block(self, **overrides) -> dict:
        row = {
            "id": self._id(),
            "start_date": START_DATE.isoformat(),
            "weeks": 4,
            "deload_week": 4,
            "status": "active",
            "rationale": "synthetic block",
            "agent_call_id": None,
        }
        return row | overrides

    def slot(self, block_id: int, day_index: int, position: int, **overrides) -> dict:
        rep_min, rep_max = self.rng.choice(REP_RANGES)
        row = {
            "id": self._id(),
            "block_id": block_id,
            "day_index": day_index,
            "position": position,
            "exercise_id": self.rng.randint(1, 40),
            "sets": self.rng.randint(2, 4),
            "rep_min": rep_min,
            "rep_max": rep_max,
            "target_rir": self.rng.randint(0, 3),
        }
        return row | overrides

    def session(self, block_id: int, week: int, day_index: int, **overrides) -> dict:
        day = START_DATE + timedelta(weeks=week - 1, days=day_index)
        row = {
            "id": self._id(),
            "block_id": block_id,
            "week": week,
            "day_index": day_index,
            "date": day.isoformat(),
            "status": "completed",
            "notes": None,
        }
        return row | overrides

    def sets(self, session: dict, slot: dict, logged: bool = True, **overrides) -> list[dict]:
        """One prescribed (and, if `logged`, performed) working set per slot set."""
        rng = self.rng
        weight = rng.randint(4, 60) * rng.choice(INCREMENTS_KG)
        rows = []
        for set_index in range(slot["sets"]):
            row = {
                "id": self._id(),
                "session_id": session["id"],
                "slot_id": slot["id"],
                "exercise_id": slot["exercise_id"],
                "set_index": set_index,
                "set_type": "working",
                "presc_weight_kg": weight,
                "presc_reps_min": slot["rep_min"],
                "presc_reps_max": slot["rep_max"],
                "presc_rir": slot["target_rir"],
                "load_modifier": "none",
                "actual_weight_kg": weight if logged else None,
                "actual_reps": rng.randint(slot["rep_min"], slot["rep_max"]) if logged else None,
                "actual_rir": rng.randint(0, 4) if logged else None,
                "pain": 0,
                "logged_at": f"{session['date']}T18:00:00" if logged else None,
            }
            rows.append(row | overrides)
        return rows

    def training_block(self, days_per_week: int = 3, slots_per_day: int = 4) -> dict:
        """A block with its slots, and one logged session per build-week day."""
        block = self.block()
        slots = [
            self.slot(block["id"], day, position)
            for day in range(days_per_week)
            for position in range(slots_per_day)
        ]
        sessions, set_entries = [], []
        for week in range(1, block["deload_week"]):
            for day in range(days_per_week):
                session = self.session(block["id"], week, day)
                sessions.append(session)
                for slot in slots:
                    if slot["day_index"] == day:
                        set_entries.extend(self.sets(session, slot))
        return {
            "block": block,
            "slots": slots,
            "sessions": sessions,
            "set_entries": set_entries,
        }
