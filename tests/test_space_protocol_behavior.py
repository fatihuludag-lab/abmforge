from __future__ import annotations

from dataclasses import dataclass

import pytest

from abmforge.world import ContinuousSpace, GridWorld, NetworkSpace, SpaceProtocol


@dataclass
class DummyAgent:
    unique_id: int


def test_gridworld_satisfies_space_protocol() -> None:
    assert isinstance(GridWorld(5, 5), SpaceProtocol)


def test_networkspace_satisfies_space_protocol() -> None:
    assert isinstance(NetworkSpace(), SpaceProtocol)


def test_continuousspace_satisfies_space_protocol() -> None:
    assert isinstance(ContinuousSpace(10.0, 10.0), SpaceProtocol)


def test_gridworld_place_move_remove_contract() -> None:
    space = GridWorld(5, 5)
    agent = DummyAgent(1)

    space.place(agent, (1, 1))

    assert space.position_of(agent) == (1, 1)
    assert space.agents_at((1, 1)) == [agent]
    assert agent.world is space
    assert agent.pos == (1, 1)

    space.move(agent, (2, 2))

    assert space.position_of(agent) == (2, 2)
    assert space.agents_at((1, 1)) == []
    assert space.agents_at((2, 2)) == [agent]
    assert agent.pos == (2, 2)

    space.remove(agent)

    with pytest.raises(KeyError):
        space.position_of(agent)

    assert not hasattr(agent, "pos")


def test_networkspace_place_move_remove_contract() -> None:
    space = NetworkSpace()
    agent = DummyAgent(1)

    space.add_edge("a", "b")
    space.place(agent, "a")

    assert space.position_of(agent) == "a"
    assert space.agents_at("a") == [agent]
    assert agent.world is space
    assert agent.pos == "a"

    space.move(agent, "b")

    assert space.position_of(agent) == "b"
    assert space.agents_at("a") == []
    assert space.agents_at("b") == [agent]
    assert agent.pos == "b"

    space.remove(agent)

    with pytest.raises(KeyError):
        space.position_of(agent)

    assert not hasattr(agent, "pos")


def test_continuousspace_place_move_remove_contract() -> None:
    space = ContinuousSpace(10.0, 10.0)
    agent = DummyAgent(1)

    space.place(agent, (1.0, 1.0))

    assert space.position_of(agent) == (1.0, 1.0)
    assert space.agents_at((1.0, 1.0)) == [agent]
    assert agent.world is space
    assert agent.pos == (1.0, 1.0)

    space.move(agent, (2.0, 2.0))

    assert space.position_of(agent) == (2.0, 2.0)
    assert space.agents_at((1.0, 1.0)) == []
    assert space.agents_at((2.0, 2.0)) == [agent]
    assert agent.pos == (2.0, 2.0)

    space.remove(agent)

    with pytest.raises(KeyError):
        space.position_of(agent)

    assert not hasattr(agent, "pos")


def test_gridworld_neighbors_exclude_source_by_default() -> None:
    space = GridWorld(5, 5)
    source = DummyAgent(1)
    neighbor = DummyAgent(2)

    space.place(source, (2, 2))
    space.place(neighbor, (2, 3))

    neighbors = space.neighbors(source)

    assert neighbor in neighbors
    assert source not in neighbors


def test_networkspace_neighbors_exclude_source_by_default() -> None:
    space = NetworkSpace()
    source = DummyAgent(1)
    neighbor = DummyAgent(2)

    space.add_edge("a", "b")
    space.place(source, "a")
    space.place(neighbor, "b")

    neighbors = space.neighbors(source)

    assert neighbor in neighbors
    assert source not in neighbors


def test_continuousspace_neighbors_exclude_source_by_default() -> None:
    space = ContinuousSpace(10.0, 10.0)
    source = DummyAgent(1)
    neighbor = DummyAgent(2)

    space.place(source, (1.0, 1.0))
    space.place(neighbor, (1.0, 2.0))

    neighbors = space.neighbors(source, radius=2.0)

    assert neighbor in neighbors
    assert source not in neighbors


def test_gridworld_rejects_duplicate_placement() -> None:
    space = GridWorld(5, 5)
    agent = DummyAgent(1)

    space.place(agent, (1, 1))

    with pytest.raises(ValueError, match="agent is already placed"):
        space.place(agent, (2, 2))


def test_continuousspace_rejects_duplicate_placement() -> None:
    space = ContinuousSpace(10.0, 10.0)
    agent = DummyAgent(1)

    space.place(agent, (1.0, 1.0))

    with pytest.raises(ValueError, match="agent is already placed"):
        space.place(agent, (2.0, 2.0))


def test_networkspace_replacement_placement_moves_existing_agent() -> None:
    space = NetworkSpace()
    agent = DummyAgent(1)

    space.place(agent, "a")
    space.place(agent, "b")

    assert space.position_of(agent) == "b"
    assert space.agents_at("a") == []
    assert space.agents_at("b") == [agent]


def test_gridworld_torus_normalizes_positions() -> None:
    space = GridWorld(5, 5, torus=True)
    agent = DummyAgent(1)

    space.place(agent, (5, 6))

    assert space.position_of(agent) == (0, 1)


def test_continuousspace_torus_normalizes_positions() -> None:
    space = ContinuousSpace(10.0, 10.0, torus=True)
    agent = DummyAgent(1)

    space.place(agent, (11.0, 12.0))

    assert space.position_of(agent) == (1.0, 2.0)


def test_gridworld_non_torus_rejects_out_of_bounds_position() -> None:
    space = GridWorld(5, 5)
    agent = DummyAgent(1)

    with pytest.raises(ValueError, match="position out of bounds"):
        space.place(agent, (5, 5))


def test_continuousspace_non_torus_rejects_out_of_bounds_position() -> None:
    space = ContinuousSpace(10.0, 10.0)
    agent = DummyAgent(1)

    with pytest.raises(ValueError, match="position out of bounds"):
        space.place(agent, (11.0, 1.0))


def test_networkspace_neighbor_nodes_and_degree() -> None:
    space = NetworkSpace()

    space.add_edge("a", "b")
    space.add_edge("a", "c")

    assert set(space.neighbor_nodes("a")) == {"b", "c"}
    assert space.degree("a") == 2
