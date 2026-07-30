from __future__ import annotations

from collections import defaultdict
from typing import Any

from abmforge.world._integrity import (
    clear_spatial_attributes,
    ensure_new_placement,
    resolve_placed_agent,
)


class NetworkSpace:
    """Simple graph-based space for network ABMs.

    This implementation avoids a mandatory NetworkX dependency.
    NetworkX integration can be added later as an optional backend.
    """

    def __init__(self) -> None:
        self._adjacency: dict[
            Any,
            dict[Any, None],
        ] = defaultdict(dict)
        self._agent_positions: dict[
            int | str,
            Any,
        ] = {}
        self._node_agents: dict[
            Any,
            dict[int | str, None],
        ] = defaultdict(dict)
        self._agents: dict[
            int | str,
            Any,
        ] = {}

    def add_node(
        self,
        node_id: Any,
    ) -> None:
        self._adjacency[node_id]

    def add_edge(
        self,
        source: Any,
        target: Any,
    ) -> None:
        self.add_node(source)
        self.add_node(target)
        self._adjacency[source][target] = None
        self._adjacency[target][source] = None

    def place_agent(
        self,
        agent: Any,
        node_id: Any,
    ) -> None:
        agent_id = agent.unique_id

        if agent_id in self._agent_positions:
            resolve_placed_agent(
                agent,
                positions=self._agent_positions,
                agents=self._agents,
            )
            self.move_agent(
                agent,
                node_id,
            )
            return

        ensure_new_placement(
            agent,
            space=self,
            positions=self._agent_positions,
            agents=self._agents,
        )

        self.add_node(node_id)
        self._agents[agent_id] = agent
        self._agent_positions[agent_id] = node_id
        self._node_agents[node_id][agent_id] = None
        agent.world = self
        agent.pos = node_id

    def place(
        self,
        agent: Any,
        node_id: Any,
    ) -> None:
        """Alias for place_agent."""
        self.place_agent(
            agent,
            node_id,
        )

    def move_agent(
        self,
        agent: Any,
        node_id: Any,
    ) -> None:
        agent_id, stored, old_node = resolve_placed_agent(
            agent,
            positions=self._agent_positions,
            agents=self._agents,
        )

        self.add_node(node_id)

        del self._node_agents[old_node][agent_id]

        if not self._node_agents[old_node]:
            del self._node_agents[old_node]

        self._agent_positions[agent_id] = node_id
        self._node_agents[node_id][agent_id] = None
        stored.pos = node_id

    def move(
        self,
        agent: Any,
        node_id: Any,
    ) -> None:
        """Alias for move_agent."""
        self.move_agent(
            agent,
            node_id,
        )

    def remove(
        self,
        agent: Any,
    ) -> None:
        agent_id, stored, node_id = resolve_placed_agent(
            agent,
            positions=self._agent_positions,
            agents=self._agents,
        )

        del self._agent_positions[agent_id]
        del self._node_agents[node_id][agent_id]

        if not self._node_agents[node_id]:
            del self._node_agents[node_id]

        del self._agents[agent_id]

        clear_spatial_attributes(
            stored,
            space=self,
        )

    def position_of(
        self,
        agent: Any,
    ) -> Any:
        _, _, position = resolve_placed_agent(
            agent,
            positions=self._agent_positions,
            agents=self._agents,
        )

        return position

    def agents_at(
        self,
        node_id: Any,
    ) -> list[Any]:
        return [
            self._agents[agent_id]
            for agent_id in self._node_agents.get(
                node_id,
                {},
            )
        ]

    def neighbor_nodes(
        self,
        node_id: Any,
    ) -> list[Any]:
        return list(self._adjacency[node_id])

    def neighbors(
        self,
        agent: Any,
        *,
        include_center: bool = False,
    ) -> list[Any]:
        node_id = self.position_of(agent)
        nodes = list(self._adjacency[node_id])

        if include_center:
            nodes.append(node_id)

        result = []

        for node in nodes:
            result.extend(self.agents_at(node))

        return result

    def degree(
        self,
        node_id: Any,
    ) -> int:
        return len(self._adjacency[node_id])
