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


def test_model_from_snapshot_restores_base_model_state():
    model = Model(seed=42, parameters={"alpha": 0.5})
    model.custom_counter = 7
    model.steps = 12
    model.time = 12.0

    agent = model.agents.create(StatefulPerson, n=1, wealth=10, mood="happy")[0]

    snapshot = model.snapshot()
    restored = Model.from_snapshot(snapshot)

    assert restored.run_id == model.run_id
    assert restored.parameters == {"alpha": 0.5}
    assert restored.steps == 12
    assert restored.time == 12.0
    assert restored.custom_counter == 7

    restored_agent = restored.agents.get(agent.unique_id)

    assert restored_agent is not None
    assert restored_agent.unique_id == agent.unique_id
    assert restored_agent.wealth == 10
    assert restored_agent.mood == "happy"


def test_model_from_snapshot_rejects_unsupported_schema_version():
    snapshot = {
        "schema_version": "999",
        "run_id": "run-1",
        "parameters": {},
        "step": 0,
        "time": 0.0,
        "model_state": {},
        "agents": [],
    }

    try:
        Model.from_snapshot(snapshot)
    except ValueError as exc:
        assert "Unsupported snapshot schema version" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_model_from_snapshot_rejects_invalid_agent_state():
    snapshot = {
        "schema_version": "1.0",
        "run_id": "run-1",
        "parameters": {},
        "step": 0,
        "time": 0.0,
        "model_state": {},
        "agents": [
            {
                "agent_id": 1,
                "state": "not-a-dict",
            }
        ],
    }

    try:
        Model.from_snapshot(snapshot)
    except ValueError as exc:
        assert "state" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
