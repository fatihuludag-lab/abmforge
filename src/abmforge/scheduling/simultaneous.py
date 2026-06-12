from __future__ import annotations

from abmforge.scheduling.base import Scheduler


class SimultaneousActivation(Scheduler):
    """Call step() for all agents, then advance() for all agents."""

    def step(self) -> None:
        agents = [agent for agent in self.model.agents if getattr(agent, "is_alive", True)]

        for agent in agents:
            agent.step()

        for agent in agents:
            if getattr(agent, "is_alive", True) and hasattr(agent, "advance"):
                agent.advance()
