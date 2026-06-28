from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from abmforge.core.agent import Agent
    from abmforge.core.model import Model

from abmforge.scheduling.base import Scheduler


def _validate_stages(stages: Sequence[str]) -> list[str]:
    if isinstance(stages, (str, bytes)):
        raise ValueError("stages must be a sequence of stage names, not a string")

    validated = list(stages)
    if not validated:
        raise ValueError("StagedActivation requires at least one stage")

    for index, stage in enumerate(validated):
        if not isinstance(stage, str) or not stage.strip():
            raise ValueError(f"stages[{index}] must be a non-empty string")

    return validated


def _call_model_stage_hook(model: Model, hook_name: str, stage: str) -> None:
    hook: Any = getattr(model, hook_name, None)
    if hook is None:
        return
    if not callable(hook):
        raise TypeError(f"model.{hook_name} must be callable when defined")
    hook(stage)


def _get_stage_method(agent: Agent, stage: str) -> Any:
    method: Any = getattr(agent, stage, None)
    if not callable(method):
        agent_id = getattr(agent, "unique_id", "<unknown>")
        raise AttributeError(
            f"Agent {agent_id!r} of type {type(agent).__name__} "
            f"does not define callable stage method {stage!r}"
        )
    return method


class StagedActivation(Scheduler):
    """Activate agents through named stages.

    Parameters
    ----------
    model:
        Model whose living agents will be activated.
    stages:
        Non-empty sequence of method names to call on each living agent.
    shuffle:
        If true, shuffle the living-agent snapshot independently for each stage
        using the model-level random number generator.

    Optional model hooks
    --------------------
    If the model defines callable ``before_stage(stage)`` or
    ``after_stage(stage)`` hooks, they are called around each stage.
    """

    def __init__(
        self,
        model: Model,
        stages: Sequence[str],
        *,
        shuffle: bool = False,
    ) -> None:
        super().__init__(model)
        self.stages = _validate_stages(stages)
        self.shuffle = shuffle

    def to_metadata(self) -> dict[str, object]:
        """Return JSON-serializable staged scheduler audit metadata."""

        metadata = super().to_metadata()
        metadata.update(
            {
                "stages": list(self.stages),
                "shuffle": self.shuffle,
            }
        )
        return metadata

    def step(self) -> None:
        agents = [agent for agent in self.model.agents if getattr(agent, "is_alive", True)]
        for stage in self.stages:
            _call_model_stage_hook(self.model, "before_stage", stage)

            stage_agents = list(agents)
            if self.shuffle:
                order = self.model.rng.permutation(len(stage_agents))
                stage_agents = [stage_agents[int(i)] for i in order]

            for agent in stage_agents:
                if getattr(agent, "is_alive", True):
                    method = _get_stage_method(agent, stage)
                    method()

            _call_model_stage_hook(self.model, "after_stage", stage)
