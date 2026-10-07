from tests.factories import Factory


def test_same_seed_gives_same_data():
    assert Factory(7).training_block() == Factory(7).training_block()
    assert Factory(7).profile() == Factory(7).profile()


def test_different_seeds_differ():
    assert Factory(7).training_block() != Factory(8).training_block()


def test_training_block_shape():
    data = Factory().training_block(days_per_week=3, slots_per_day=4)
    assert len(data["slots"]) == 12
    assert len(data["sessions"]) == 9  # 3 build weeks x 3 days
    assert len(data["set_entries"]) == 3 * sum(s["sets"] for s in data["slots"])
    for row in data["set_entries"]:
        assert row["presc_reps_min"] <= row["actual_reps"] <= row["presc_reps_max"]
        assert 0 <= row["pain"] <= 10


def test_unlogged_sets_have_no_actuals():
    factory = Factory()
    block = factory.block()
    slot = factory.slot(block["id"], 0, 0)
    session = factory.session(block["id"], 1, 0, status="planned")
    for row in factory.sets(session, slot, logged=False):
        assert row["actual_weight_kg"] is None
        assert row["actual_reps"] is None
        assert row["logged_at"] is None
