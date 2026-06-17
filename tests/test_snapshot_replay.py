from abmforge import (
    Agent,
    GridWorld,
    Model,
    attach_snapshot_hash,
    link_snapshot,
    read_snapshot,
    snapshot_hash,
    write_snapshot,
)


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
    assert "rng_state" in snapshot
    assert isinstance(snapshot["rng_state"], dict)
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


def test_snapshot_hash_is_deterministic_for_equivalent_snapshots():
    snapshot_a = {
        "schema_version": "1.0",
        "run_id": "run-1",
        "model": "Model",
        "step": 1,
        "time": 1.0,
        "parameters": {"beta": 2, "alpha": 1},
        "model_state": {"x": 10},
        "agents": [
            {
                "id": 1,
                "agent_id": 1,
                "type": "Person",
                "agent_type": "Person",
                "state": {"wealth": 10},
            }
        ],
    }

    snapshot_b = {
        "agents": [
            {
                "state": {"wealth": 10},
                "agent_type": "Person",
                "type": "Person",
                "agent_id": 1,
                "id": 1,
            }
        ],
        "model_state": {"x": 10},
        "parameters": {"alpha": 1, "beta": 2},
        "time": 1.0,
        "step": 1,
        "model": "Model",
        "run_id": "run-1",
        "schema_version": "1.0",
    }

    assert snapshot_hash(snapshot_a) == snapshot_hash(snapshot_b)


def test_snapshot_hash_changes_when_state_changes():
    snapshot = {
        "schema_version": "1.0",
        "run_id": "run-1",
        "model": "Model",
        "step": 1,
        "time": 1.0,
        "parameters": {},
        "model_state": {},
        "agents": [
            {
                "id": 1,
                "agent_id": 1,
                "type": "Person",
                "agent_type": "Person",
                "state": {"wealth": 10},
            }
        ],
    }

    changed = {
        "schema_version": "1.0",
        "run_id": "run-1",
        "model": "Model",
        "step": 1,
        "time": 1.0,
        "parameters": {},
        "model_state": {},
        "agents": [
            {
                "id": 1,
                "agent_id": 1,
                "type": "Person",
                "agent_type": "Person",
                "state": {"wealth": 11},
            }
        ],
    }

    assert snapshot_hash(snapshot) != snapshot_hash(changed)


def test_restored_snapshot_hash_matches_original_snapshot_hash():
    model = Model(seed=42, parameters={"alpha": 0.5})
    model.custom_counter = 7
    model.steps = 3
    model.time = 3.0
    model.agents.create(StatefulPerson, n=1, wealth=10, mood="happy")

    snapshot = model.snapshot()
    restored = Model.from_snapshot(snapshot)

    assert snapshot_hash(restored.snapshot(), include_metadata=False) == snapshot_hash(
        snapshot,
        include_metadata=False,
    )


def test_snapshot_hash_can_ignore_type_metadata():
    snapshot_a = {
        "schema_version": "1.0",
        "run_id": "run-1",
        "model": "CustomModel",
        "model_name": "CustomModel",
        "step": 0,
        "time": 0.0,
        "parameters": {},
        "model_state": {},
        "agents": [
            {
                "id": 1,
                "agent_id": 1,
                "type": "CustomAgent",
                "agent_type": "CustomAgent",
                "state": {"wealth": 10},
            }
        ],
    }

    snapshot_b = {
        "schema_version": "1.0",
        "run_id": "run-1",
        "model": "Model",
        "model_name": "Model",
        "step": 0,
        "time": 0.0,
        "parameters": {},
        "model_state": {},
        "agents": [
            {
                "id": 1,
                "agent_id": 1,
                "type": "Agent",
                "agent_type": "Agent",
                "state": {"wealth": 10},
            }
        ],
    }

    assert snapshot_hash(snapshot_a) != snapshot_hash(snapshot_b)
    assert snapshot_hash(snapshot_a, include_metadata=False) == snapshot_hash(
        snapshot_b,
        include_metadata=False,
    )


def test_model_from_snapshot_restores_rng_state():
    model = Model(seed=42)

    _ = model.rng.random(5)
    snapshot = model.snapshot()

    restored = Model.from_snapshot(snapshot)

    assert model.rng.random() == restored.rng.random()


def test_model_from_snapshot_rejects_invalid_rng_state():
    snapshot = {
        "schema_version": "1.0",
        "run_id": "run-1",
        "parameters": {},
        "rng_state": "not-a-dict",
        "step": 0,
        "time": 0.0,
        "model_state": {},
        "agents": [],
    }

    try:
        Model.from_snapshot(snapshot)
    except ValueError as exc:
        assert "rng_state" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_restored_model_continues_with_same_rng_sequence():
    model = Model(seed=42)

    # Advance RNG before snapshot.
    pre_snapshot_values = model.rng.random(5)
    assert len(pre_snapshot_values) == 5

    snapshot = model.snapshot()
    restored = Model.from_snapshot(snapshot)

    original_next_values = model.rng.random(10)
    restored_next_values = restored.rng.random(10)

    assert original_next_values.tolist() == restored_next_values.tolist()


class RandomWalkAgent(Agent):
    pass


class RandomWalkModel(Model):
    def setup(self) -> None:
        if len(self.agents) == 0:
            self.agents.create(RandomWalkAgent, n=1, position=0)

    def step(self) -> None:
        for agent in self.agents:
            move = int(self.rng.choice([-1, 1]))
            agent.position += move


def test_restored_model_continues_to_same_agent_state_with_rng_restore():
    model = RandomWalkModel(seed=42)
    model.setup()
    model.run_for(5)

    snapshot = model.snapshot()
    restored = RandomWalkModel.from_snapshot(snapshot)

    model.run_for(10)
    restored.run_for(10)

    original_agent = next(iter(model.agents))
    restored_agent = next(iter(restored.agents))

    assert original_agent.position == restored_agent.position


def test_snapshot_contains_provenance_metadata():
    model = Model(seed=42)

    snapshot = model.snapshot()

    assert "snapshot_id" in snapshot
    assert "created_at" in snapshot
    assert "parent_snapshot" in snapshot
    assert "experiment_id" in snapshot
    assert "manifest_hash" in snapshot


def test_snapshot_hash_can_be_attached():
    model = Model(seed=42)

    snapshot = model.snapshot()

    snapshot = attach_snapshot_hash(snapshot)

    assert "snapshot_hash" in snapshot


def test_link_snapshot_sets_parent_snapshot_id():
    model = Model(seed=42)

    parent = model.snapshot()
    child = model.snapshot()

    linked = link_snapshot(parent, child)

    assert linked["parent_snapshot"] == parent["snapshot_id"]
    assert child["parent_snapshot"] is None


def test_link_snapshot_does_not_mutate_child_snapshot():
    model = Model(seed=42)

    parent = model.snapshot()
    child = model.snapshot()

    linked = link_snapshot(parent, child)

    assert linked is not child
    assert linked["parent_snapshot"] == parent["snapshot_id"]
    assert child["parent_snapshot"] is None


def test_link_snapshot_rejects_parent_without_snapshot_id():
    parent = {
        "schema_version": "1.0",
        "run_id": "run-1",
    }
    child = {
        "schema_version": "1.0",
        "run_id": "run-1",
        "parent_snapshot": None,
    }

    try:
        link_snapshot(parent, child)
    except ValueError as exc:
        assert "snapshot_id" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
