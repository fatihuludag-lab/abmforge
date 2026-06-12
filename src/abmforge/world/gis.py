from __future__ import annotations

import math
from typing import Any

Position = tuple[float, float]


class GISSpace:
    """Lightweight geographic space.

    Coordinates are stored as (longitude, latitude).
    """

    def __init__(self) -> None:
        self._positions: dict[int | str, Position] = {}
        self._agents: dict[int | str, Any] = {}

    def place(self, agent: Any, position: Position) -> None:
        self._positions[agent.unique_id] = position
        self._agents[agent.unique_id] = agent

        agent.world = self
        agent.pos = position

    def move(self, agent: Any, position: Position) -> None:
        self._positions[agent.unique_id] = position
        agent.pos = position

    def remove(self, agent: Any) -> None:
        self._positions.pop(agent.unique_id, None)
        self._agents.pop(agent.unique_id, None)

    def position_of(self, agent: Any) -> Position:
        return self._positions[agent.unique_id]

    def distance(self, a: Any, b: Any) -> float:
        """Great-circle distance in kilometers."""
        lon1, lat1 = self.position_of(a)
        lon2, lat2 = self.position_of(b)

        radius = 6371.0

        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)

        dlat = lat2 - lat1
        dlon = math.radians(lon2 - lon1)

        h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2

        return 2 * radius * math.asin(math.sqrt(h))

    def neighbors(
        self,
        agent: Any,
        *,
        radius_km: float,
    ) -> list[Any]:
        found = []

        for other in self._agents.values():
            if other.unique_id == agent.unique_id:
                continue

            if self.distance(agent, other) <= radius_km:
                found.append(other)

        return found

    def to_geojson(self) -> dict[str, Any]:
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
