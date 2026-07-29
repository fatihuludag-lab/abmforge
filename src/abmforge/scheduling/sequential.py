from __future__ import annotations

from abmforge.scheduling.base import Scheduler


class SequentialActivation(Scheduler):
    """Activate agents in insertion order."""

    def step(self) -> None:
        for agent in list(self.model.agents):
            if self.model.agents._is_activation_eligible(agent):
                agent.step()
