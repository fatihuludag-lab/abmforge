from __future__ import annotations

from typing import TYPE_CHECKING, cast

from abmforge import Agent

if TYPE_CHECKING:
    from model.model import SegregationTemplateModel


class Resident(Agent):
    """Resident in a simple Schelling-style segregation model."""

    def evaluate(self) -> None:
        model = cast("SegregationTemplateModel", self.model)
        neighbors = [
            neighbor
            for neighbor in self.neighbors(
                radius=model.neighborhood_radius,
                include_center=False,
            )
            if isinstance(neighbor, Resident)
        ]

        if not neighbors:
            self.similarity = 1.0
            self.happy = True
            self.will_relocate = False
            return

        similar_neighbors = sum(int(neighbor.group == self.group) for neighbor in neighbors)
        self.similarity = similar_neighbors / len(neighbors)
        self.happy = self.similarity >= model.homophily_threshold
        self.will_relocate = not self.happy

    def relocate(self) -> None:
        model = cast("SegregationTemplateModel", self.model)

        if not self.will_relocate or not model.empty_positions:
            return

        old_position = getattr(self, "pos", None)
        if old_position is None:
            return

        empty_positions = sorted(model.empty_positions)
        target = empty_positions[int(self.rng.integers(0, len(empty_positions)))]

        model.empty_positions.remove(target)
        model.empty_positions.add(old_position)
        model.world.move(self, target)
        model.relocation_count += 1
