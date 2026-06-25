from __future__ import annotations

from typing import TYPE_CHECKING, cast

from abmforge import Agent

if TYPE_CHECKING:
    from model.model import NetworkTemplateModel


class NetworkResident(Agent):
    """Resident that can adopt through local network exposure or broadcast."""

    def decide(self) -> None:
        model = cast("NetworkTemplateModel", self.model)

        if self.adopted:
            self.will_adopt = True
            return

        neighbors = model.world.neighbors(self, include_center=False)

        if neighbors:
            adopted_share = sum(
                int(getattr(neighbor, "adopted", False)) for neighbor in neighbors
            ) / len(neighbors)
        else:
            adopted_share = 0.0

        threshold_met = adopted_share >= self.threshold
        broadcast_hit = self.rng.random() < model.broadcast_probability

        self.will_adopt = threshold_met or broadcast_hit

    def adopt(self) -> None:
        if self.will_adopt:
            self.adopted = True
