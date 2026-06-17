from abmforge import Agent, GridWorld, Model, read_snapshot, write_snapshot


class Person(Agent):
    pass


class StatefulPerson(Agent):
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


def test_snapshot_schema_v1_contains_model_parameters_and_agent_state():
    model = Model(seed=42, parameters={"alpha": 0.5})
    model.custom_counter = 7

    agent = model.agents.create(StatefulPerson, n=1, wealth=10, mood="happy")[0]

    snapshot = model.snapshot()

    assert snapshot["schema_version"] == "1.0"
    assert snapshot["run_id"] == model.run_id
    assert snapshot["model"] == "Model"
    assert snapshot["model_name"] == "Model"
    assert snapshot["step"] == model.steps
    assert snapshot["time"] == model.time
    assert snapshot["parameters"] == {"alpha": 0.5}
    assert snapshot["model_state"] == {"custom_counter": 7}

    assert snapshot["agents"][0]["id"] == agent.unique_id
    assert snapshot["agents"][0]["agent_id"] == agent.unique_id
    assert snapshot["agents"][0]["type"] == "StatefulPerson"
    assert snapshot["agents"][0]["agent_type"] == "StatefulPerson"
    assert snapshot["agents"][0]["state"] == {
        "wealth": 10,
        "mood": "happy",
    }


def test_snapshot_schema_v1_excludes_framework_internal_state():
    model = Model(seed=42)
    model._private_value = "hidden"
    model.public_value = "visible"

    snapshot = model.snapshot()

    assert snapshot["model_state"] == {"public_value": "visible"}
    assert "_private_value" not in snapshot["model_state"]
