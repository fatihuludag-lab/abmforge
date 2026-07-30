from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pytest

from abmforge import (
    Agent,
    ContinuousSpace,
    GISSpace,
    GridWorld,
    Model,
    NetworkSpace,
)
from abmforge.core.agent_lifecycle import (
    ACTIVE,
    REMOVED,
)


@dataclass(frozen=True)
class _SpaceCase:
    name: str
    factory: Callable[[], Any]
    first_position: Any
    second_position: Any


_SPACE_CASES = [
    _SpaceCase(
        name="grid",
        factory=lambda: GridWorld(
            width=4,
            height=4,
        ),
        first_position=(1, 1),
        second_position=(2, 2),
    ),
    _SpaceCase(
        name="continuous",
        factory=lambda: ContinuousSpace(
            width=10.0,
            height=10.0,
        ),
        first_position=(1.0, 1.0),
        second_position=(2.0, 2.0),
    ),
    _SpaceCase(
        name="gis",
        factory=GISSpace,
        first_position=(32.0, 39.0),
        second_position=(33.0, 40.0),
    ),
    _SpaceCase(
        name="network",
        factory=NetworkSpace,
        first_position="node-a",
        second_position="node-b",
    ),
]


@pytest.fixture(
    params=_SPACE_CASES,
    ids=lambda case: case.name,
)
def space_case(
    request: pytest.FixtureRequest,
) -> _SpaceCase:
    return request.param


def _placed_agent(
    case: _SpaceCase,
    *,
    attach_world: bool = True,
) -> tuple[Model, Any, Agent]:
    model = Model(seed=42)
    world = case.factory()

    if attach_world:
        model.world = world

    agent = Agent(
        model=model,
        unique_id=1,
    )
    model.agents.add(agent)
    world.place(
        agent,
        case.first_position,
    )

    return model, world, agent


@pytest.mark.parametrize(
    "remove_by_id",
    [
        False,
        True,
    ],
)
def test_collection_remove_runs_complete_lifecycle_cleanup(
    space_case: _SpaceCase,
    remove_by_id: bool,
) -> None:
    model, world, agent = _placed_agent(space_case)

    event = model.events.schedule_after(
        1,
        callback=lambda: None,
        owner=agent.unique_id,
        tags=["owned"],
    )

    target: Agent | int | str = agent.unique_id if remove_by_id else agent

    removed = model.agents.remove(target)

    assert removed is agent
    assert agent not in model.agents
    assert agent.is_alive is False
    assert agent.lifecycle_status == REMOVED
    assert not hasattr(agent, "pos")
    assert not hasattr(agent, "world")

    with pytest.raises(KeyError):
        world.position_of(agent)

    assert world.agents_at(space_case.first_position) == []
    assert model.events.events_for_owner(agent.unique_id) == []

    lifecycle_records = [
        record
        for record in model.record.dataset.lifecycle_records
        if (record["event"] == "agent_removed" and record["agent_id"] == agent.unique_id)
    ]

    assert len(lifecycle_records) == 1

    assert any(
        record["event_id"] == event.event_id and record["status"] == "cancelled"
        for record in model.record.dataset.event_records
    )


def test_same_id_replacement_has_no_stale_space_state(
    space_case: _SpaceCase,
) -> None:
    model, world, old = _placed_agent(space_case)

    removed = model.agents.remove(old)

    assert removed is old

    replacement = Agent(
        model=model,
        unique_id=old.unique_id,
    )

    model.agents.add(replacement)
    world.place(
        replacement,
        space_case.first_position,
    )

    assert model.agents.get(old.unique_id) is replacement

    assert world.position_of(replacement) == space_case.first_position

    assert world.agents_at(space_case.first_position) == [replacement]

    assert old.is_alive is False
    assert old.lifecycle_status == REMOVED
    assert not hasattr(old, "pos")
    assert not hasattr(old, "world")

    assert replacement.is_alive is True
    assert replacement.lifecycle_status == ACTIVE
    assert replacement.world is world


@pytest.mark.parametrize(
    ("is_alive", "lifecycle_status"),
    [
        (False, ACTIVE),
        (True, REMOVED),
        (False, REMOVED),
    ],
)
def test_collection_rejects_non_active_agent(
    is_alive: bool,
    lifecycle_status: str,
) -> None:
    model = Model(seed=42)
    agent = Agent(
        model=model,
        unique_id=1,
    )
    agent.is_alive = is_alive
    agent.lifecycle_status = lifecycle_status  # type: ignore[assignment]

    with pytest.raises(
        ValueError,
        match="active living agent",
    ):
        model.agents.add(agent)

    assert agent not in model.agents


def test_removed_agent_cannot_be_readded() -> None:
    model = Model(seed=42)
    agent = model.agents.create(
        Agent,
        n=1,
    )[0]

    model.remove_agent(agent)

    with pytest.raises(
        ValueError,
        match="active living agent",
    ):
        model.agents.add(agent)

    assert agent not in model.agents


def test_repeated_removal_is_fail_closed_without_duplicate_record() -> None:
    model = Model(seed=42)
    agent = model.agents.create(
        Agent,
        n=1,
    )[0]

    model.remove_agent(agent)

    record_count = len(model.record.dataset.lifecycle_records)

    with pytest.raises(
        KeyError,
        match="unknown agent id",
    ):
        model.remove_agent(agent)

    assert len(model.record.dataset.lifecycle_records) == record_count


def test_model_remove_rejects_same_model_impostor() -> None:
    model = Model(seed=42)

    stored = Agent(
        model=model,
        unique_id=1,
    )
    impostor = Agent(
        model=model,
        unique_id=1,
    )

    model.agents.add(stored)

    with pytest.raises(
        ValueError,
        match="current agent object",
    ):
        model.remove_agent(impostor)

    assert model.agents.get(1) is stored
    assert stored.is_alive is True
    assert stored.lifecycle_status == ACTIVE


def test_model_removes_agent_from_actual_agent_world(
    space_case: _SpaceCase,
) -> None:
    model, world, agent = _placed_agent(
        space_case,
        attach_world=False,
    )

    assert model.world is None
    assert agent.world is world

    model.remove_agent(agent)

    with pytest.raises(KeyError):
        world.position_of(agent)

    assert not hasattr(agent, "pos")
    assert not hasattr(agent, "world")
    assert agent not in model.agents


def test_direct_space_remove_clears_spatial_attributes(
    space_case: _SpaceCase,
) -> None:
    model, world, agent = _placed_agent(space_case)

    world.remove(agent)

    with pytest.raises(KeyError):
        world.position_of(agent)

    assert world.agents_at(space_case.first_position) == []
    assert not hasattr(agent, "pos")
    assert not hasattr(agent, "world")

    # Direct spatial removal is not lifecycle removal.
    assert model.agents.get(agent.unique_id) is agent
    assert agent.is_alive is True
    assert agent.lifecycle_status == ACTIVE


@pytest.mark.parametrize(
    "operation",
    [
        "position_of",
        "move",
        "remove",
    ],
)
def test_space_rejects_same_id_different_object(
    space_case: _SpaceCase,
    operation: str,
) -> None:
    model, world, stored = _placed_agent(space_case)

    impostor = Agent(
        model=model,
        unique_id=stored.unique_id,
    )

    with pytest.raises(
        ValueError,
        match="different agent object",
    ):
        if operation == "position_of":
            world.position_of(impostor)
        elif operation == "move":
            world.move(
                impostor,
                space_case.second_position,
            )
        else:
            world.remove(impostor)

    assert world.position_of(stored) == space_case.first_position

    assert world.agents_at(space_case.first_position) == [stored]

    assert stored.world is world
    assert stored.pos == space_case.first_position


def test_network_replacing_placement_of_same_object_moves_agent() -> None:
    space = NetworkSpace()
    agent = Agent(
        model=Model(seed=42),
        unique_id=1,
    )

    space.place(
        agent,
        "node-a",
    )
    space.place(
        agent,
        "node-b",
    )

    assert space.position_of(agent) == "node-b"
    assert space.agents_at("node-a") == []
    assert space.agents_at("node-b") == [agent]
    assert agent.world is space
    assert agent.pos == "node-b"


def test_network_rejects_different_object_with_placed_id() -> None:
    model = Model(seed=42)
    space = NetworkSpace()

    stored = Agent(
        model=model,
        unique_id=1,
    )
    replacement = Agent(
        model=model,
        unique_id=1,
    )

    space.place(
        stored,
        "node-a",
    )

    with pytest.raises(
        ValueError,
        match="different agent object",
    ):
        space.place(
            replacement,
            "node-b",
        )

    assert space.position_of(stored) == "node-a"
    assert space.agents_at("node-a") == [stored]
    assert space.agents_at("node-b") == []
    assert stored.world is space
    assert stored.pos == "node-a"
    assert not hasattr(replacement, "world")
    assert not hasattr(replacement, "pos")


class _FailingRemovalSpace:
    def place(
        self,
        agent: Agent,
        position: Any,
    ) -> None:
        agent.world = self
        agent.pos = position

    def position_of(
        self,
        agent: Agent,
    ) -> Any:
        return agent.pos

    def remove(
        self,
        agent: Agent,
    ) -> None:
        raise RuntimeError("space removal failed")


def test_space_failure_does_not_partially_remove_agent() -> None:
    model = Model(seed=42)
    world = _FailingRemovalSpace()
    model.world = world

    agent = model.agents.create(
        Agent,
        n=1,
    )[0]
    world.place(
        agent,
        "position",
    )

    model.events.schedule_after(
        1,
        callback=lambda: None,
        owner=agent.unique_id,
    )

    with pytest.raises(
        RuntimeError,
        match="space removal failed",
    ):
        model.remove_agent(agent)

    assert model.agents.get(agent.unique_id) is agent
    assert agent.is_alive is True
    assert agent.lifecycle_status == ACTIVE
    assert agent.world is world
    assert agent.pos == "position"
    assert model.events.pending_count() == 1

    assert not any(
        record["event"] == "agent_removed" for record in model.record.dataset.lifecycle_records
    )


def test_space_rejects_agent_already_placed_in_another_space(
    space_case: _SpaceCase,
) -> None:
    model = Model(seed=42)
    first_space = space_case.factory()
    second_space = space_case.factory()

    agent = Agent(
        model=model,
        unique_id=1,
    )

    first_space.place(
        agent,
        space_case.first_position,
    )

    with pytest.raises(
        ValueError,
        match="another space",
    ):
        second_space.place(
            agent,
            space_case.second_position,
        )

    assert first_space.position_of(agent) == space_case.first_position

    assert first_space.agents_at(space_case.first_position) == [agent]

    assert second_space.agents_at(space_case.second_position) == []

    assert agent.world is first_space
    assert agent.pos == space_case.first_position
