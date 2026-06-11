from abmforge import Agent, GridWorld, Model, read_snapshot, write_snapshot


class Person(Agent):
    pass


def test_write_and_read_snapshot(tmp_path):
    model = Model(seed=42)
    model.world = GridWorld(width=5, height=5)

    agent = model.agents.create(Person, n=1, wealth=10)[0]
    model.world.place(agent, (2, 3))

    snapshot = model.snapshot()
    path = write_snapshot(snapshot, tmp_path / "snapshot.json")

    loaded = read_snapshot(path)

    assert loaded["run_id"] == model.run_id
    assert loaded["step"] == model.steps
    assert loaded["model"] == "Model"
    assert loaded["agents"][0]["id"] == agent.unique_id
    assert loaded["agents"][0]["position"] == [2, 3]


def test_read_snapshot_returns_dict(tmp_path):
    path = tmp_path / "snapshot.json"
    path.write_text('{"run_id": "run-1", "step": 0}', encoding="utf-8")

    snapshot = read_snapshot(path)

    assert snapshot == {"run_id": "run-1", "step": 0}
