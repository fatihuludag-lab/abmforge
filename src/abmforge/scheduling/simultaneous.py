from __future__ import annotations

from abmforge.scheduling.base import Scheduler


class SimultaneousActivation(Scheduler):
    """Call step() for all agents, then advance() for all agents."""

    def step(self) -> None:
        agents = [
            agent for agent in self.model.agents if self.model.agents._is_activation_eligible(agent)
        ]

        for agent in agents:
            if self.model.agents._is_activation_eligible(agent):
                agent.step()

        for agent in agents:
            if self.model.agents._is_activation_eligible(agent) and hasattr(agent, "advance"):
                agent.advance()
