from __future__ import annotations

from abmforge.scheduling.base import Scheduler


class RandomActivation(Scheduler):
    """Activate agents using the model's named scheduler RNG stream."""

    def step(self) -> None:
        agents = [
            agent for agent in self.model.agents if self.model.agents._is_activation_eligible(agent)
        ]
        order = self.model.rng_stream("scheduler").permutation(len(agents))

        for idx in order:
            agent = agents[int(idx)]

            if self.model.agents._is_activation_eligible(agent):
                agent.step()
