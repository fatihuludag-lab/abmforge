from __future__ import annotations

from typing import TYPE_CHECKING, cast

from abmforge import Agent

if TYPE_CHECKING:
    from model.model import ResearchStudyModel


class ResearchAgent(Agent):
    """Agent that may adopt when social and external pressure exceeds threshold."""

    def step(self) -> None:
        model = cast("ResearchStudyModel", self.model)

        if self.adopted:
            return

        pressure = model.peer_influence * model.current_adoption_share + model.external_influence

        if pressure >= self.threshold:
            self.adopted = True
            model.new_adoptions += 1
