from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from abmforge.core.model import Model

from abmforge.scheduling.base import Scheduler


class StagedActivation(Scheduler):
    """Activate agents through named stages."""

    def __init__(
        self,
        model: Model,
        stages: Sequence[str],
        *,
        shuffle: bool = False,
    ) -> None:
        super().__init__(model)
        self.stages = list(stages)
        self.shuffle = shuffle

    def step(self) -> None:
        agents = [agent for agent in self.model.agents if getattr(agent, "is_alive", True)]

        for stage in self.stages:
            stage_agents = list(agents)

            if self.shuffle:
                order = self.model.rng.permutation(len(stage_agents))
                stage_agents = [stage_agents[int(i)] for i in order]

            for agent in stage_agents:
                if getattr(agent, "is_alive", True):
                    method = getattr(agent, stage)
                    method()
