from __future__ import annotations

from typing import TYPE_CHECKING, cast

from abmforge import Agent

if TYPE_CHECKING:
    from model.model import GridTemplateModel


class Resident(Agent):
    """Simple resident that may transfer one wealth unit to a neighbor."""

    def step(self) -> None:
        model = cast("GridTemplateModel", self.model)

        if self.wealth <= 0:
            return

        if self.rng.random() >= model.transfer_probability:
            return

        neighbors = [
            agent
            for agent in self.neighbors(radius=1, include_center=False)
            if isinstance(agent, Resident)
        ]

        if not neighbors:
            return

        other = neighbors[int(self.rng.integers(0, len(neighbors)))]
        self.wealth -= 1
        other.wealth += 1
