from __future__ import annotations

from typing import TYPE_CHECKING, cast

from abmforge import Agent

if TYPE_CHECKING:
    from model.model import ResourceTemplateModel


class Forager(Agent):
    """Forager that moves toward nearby resources and harvests them."""

    def forage(self) -> None:
        model = cast("ResourceTemplateModel", self.model)

        if not self.active:
            return

        current = getattr(self, "pos", None)
        if current is None:
            return

        target = model.best_visible_position(current)
        if target != current:
            model.empty_positions.remove(target)
            model.empty_positions.add(current)
            model.world.move(self, target)

        harvested = model.harvest_at(target)
        self.wealth += harvested
        self.energy += harvested * model.energy_from_resource
        self.energy -= model.metabolism

        if self.energy <= 0.0:
            self.active = False
            self.energy = 0.0
