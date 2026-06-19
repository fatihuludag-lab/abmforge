from __future__ import annotations

from collections import defaultdict
from typing import Any


class NetworkSpace:
    """Simple graph-based space for network ABMs.

    This implementation avoids a mandatory NetworkX dependency.
    NetworkX integration can be added later as an optional backend.
    """

    def __init__(self) -> None:
        self._adjacency: dict[Any, set[Any]] = defaultdict(set)
        self._agent_positions: dict[int | str, Any] = {}
        self._node_agents: dict[Any, set[int | str]] = defaultdict(set)
        self._agents: dict[int | str, Any] = {}

    def add_node(self, node_id: Any) -> None:
        self._adjacency[node_id]

    def add_edge(self, source: Any, target: Any) -> None:
        self.add_node(source)
        self.add_node(target)
        self._adjacency[source].add(target)
        self._adjacency[target].add(source)

    def place_agent(self, agent: Any, node_id: Any) -> None:
        self.add_node(node_id)
        agent_id = agent.unique_id

        if agent_id in self._agent_positions:
            self.remove(agent)

        self._agents[agent_id] = agent
        self._agent_positions[agent_id] = node_id
        self._node_agents[node_id].add(agent_id)
        agent.world = self
        agent.pos = node_id

    def place(self, agent: Any, node_id: Any) -> None:
        """Alias for place_agent."""
        self.place_agent(agent, node_id)

    def move_agent(self, agent: Any, node_id: Any) -> None:
        self.add_node(node_id)
        agent_id = agent.unique_id

        old_node = self._agent_positions[agent_id]
        self._node_agents[old_node].remove(agent_id)

        self._agent_positions[agent_id] = node_id
        self._node_agents[node_id].add(agent_id)
        agent.pos = node_id

    def move(self, agent: Any, node_id: Any) -> None:
        """Alias for move_agent."""
        self.move_agent(agent, node_id)

    def remove(self, agent: Any) -> None:
        agent_id = agent.unique_id
        node_id = self._agent_positions.pop(agent_id)
        self._node_agents[node_id].remove(agent_id)
        self._agents.pop(agent_id, None)

        if hasattr(agent, "pos"):
            delattr(agent, "pos")

    def position_of(self, agent: Any) -> Any:
        return self._agent_positions[agent.unique_id]

    def agents_at(self, node_id: Any) -> list[Any]:
        return [self._agents[agent_id] for agent_id in self._node_agents[node_id]]

    def neighbor_nodes(self, node_id: Any) -> list[Any]:
        return list(self._adjacency[node_id])

    def neighbors(self, agent: Any, *, include_center: bool = False) -> list[Any]:
        node_id = self.position_of(agent)
        nodes = set(self._adjacency[node_id])

        if include_center:
            nodes.add(node_id)

        result = []
        for node in nodes:
            result.extend(self.agents_at(node))

        return result

    def degree(self, node_id: Any) -> int:
        return len(self._adjacency[node_id])
