from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from abmforge.world._integrity import (
    clear_spatial_attributes,
    ensure_new_placement,
    resolve_placed_agent,
)

Position = tuple[float, float]


class GISSpace:
    """Lightweight geographic point space.

    Coordinates are stored as ``(longitude, latitude)`` tuples. GISSpace uses
    exact coordinate matching for ``agents_at()`` and great-circle distance for
    radius-based neighbor queries.
    """

    def __init__(self) -> None:
        self._positions: dict[
            int | str,
            Position,
        ] = {}
        self._position_agents: dict[
            Position,
            list[int | str],
        ] = defaultdict(list)
        self._agents: dict[
            int | str,
            Any,
        ] = {}

    def place(
        self,
        agent: Any,
        position: Position,
    ) -> None:
        """Place an agent at a geographic position."""
        ensure_new_placement(
            agent,
            space=self,
            positions=self._positions,
            agents=self._agents,
        )

        agent_id = agent.unique_id
        self._positions[agent_id] = position
        self._position_agents[position].append(agent_id)
        self._agents[agent_id] = agent
        agent.world = self
        agent.pos = position

    def move(
        self,
        agent: Any,
        position: Position,
    ) -> None:
        """Move a placed agent to a new geographic position."""
        agent_id, stored, old_position = resolve_placed_agent(
            agent,
            positions=self._positions,
            agents=self._agents,
        )

        self._position_agents[old_position].remove(agent_id)

        if not self._position_agents[old_position]:
            del self._position_agents[old_position]

        self._positions[agent_id] = position
        self._position_agents[position].append(agent_id)
        stored.pos = position

    def remove(
        self,
        agent: Any,
    ) -> None:
        """Remove a placed agent from the space."""
        agent_id, stored, position = resolve_placed_agent(
            agent,
            positions=self._positions,
            agents=self._agents,
        )

        self._position_agents[position].remove(agent_id)

        if not self._position_agents[position]:
            del self._position_agents[position]

        del self._positions[agent_id]
        del self._agents[agent_id]

        clear_spatial_attributes(
            stored,
            space=self,
        )

    def position_of(
        self,
        agent: Any,
    ) -> Position:
        """Return an agent's geographic position."""
        _, _, position = resolve_placed_agent(
            agent,
            positions=self._positions,
            agents=self._agents,
        )

        return position

    def agents_at(
        self,
        position: Position,
    ) -> list[Any]:
        """Return agents at an exact geographic position."""
        return [
            self._agents[agent_id]
            for agent_id in self._position_agents.get(
                position,
                [],
            )
        ]

    def distance(
        self,
        a: Any,
        b: Any,
    ) -> float:
        """Return great-circle distance between two placed agents in kilometers."""
        return self._distance_between_positions(
            self.position_of(a),
            self.position_of(b),
        )

    @staticmethod
    def _distance_between_positions(
        a: Position,
        b: Position,
    ) -> float:
        """Return great-circle distance between two positions in kilometers."""
        lon1, lat1 = a
        lon2, lat2 = b

        radius = 6371.0
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = lat2_rad - lat1_rad
        dlon = math.radians(lon2 - lon1)

        h = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )

        return 2 * radius * math.asin(math.sqrt(h))

    def neighbors(
        self,
        agent_or_position: Any,
        *,
        radius_km: float,
        include_center: bool = False,
    ) -> list[Any]:
        """Return agents within ``radius_km`` of an agent or position."""
        if radius_km < 0:
            raise ValueError("radius_km must be non-negative")

        if isinstance(
            agent_or_position,
            tuple,
        ):
            center = agent_or_position
            source_id = None
        else:
            center = self.position_of(agent_or_position)
            source_id = agent_or_position.unique_id

        found: list[Any] = []

        for other_id, other_position in self._positions.items():
            if source_id is not None and other_id == source_id and not include_center:
                continue

            if (
                self._distance_between_positions(
                    center,
                    other_position,
                )
                <= radius_km
            ):
                found.append(self._agents[other_id])

        return found

    def to_geojson(
        self,
    ) -> dict[str, Any]:
        """Export placed agents as a GeoJSON FeatureCollection."""
        features = []

        for agent_id, position in self._positions.items():
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "agent_id": agent_id,
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": list(position),
                    },
                }
            )

        return {
            "type": "FeatureCollection",
            "features": features,
        }
