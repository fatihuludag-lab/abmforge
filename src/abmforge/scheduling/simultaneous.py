from __future__ import annotations

from collections.abc import Callable
from typing import cast

from abmforge.core.agent import Agent
from abmforge.scheduling.base import Scheduler

_CONTRACT_ERROR = (
    "SimultaneousActivation requires every eligible agent to define "
    "callable step() and advance() methods"
)

_TwoPhaseCallbacks = tuple[
    Agent,
    Callable[[], None],
    Callable[[], None],
]


class SimultaneousActivation(Scheduler):
    """Activate eligible agents using a strict two-phase contract."""

    def step(self) -> None:
        """Run every decision callback before any commit callback."""
        callbacks = self._validated_callbacks()

        for agent, step_callback, _ in callbacks:
            if self.model.agents._is_activation_eligible(agent):
                step_callback()

        for agent, _, advance_callback in callbacks:
            if self.model.agents._is_activation_eligible(agent):
                advance_callback()

    def _validated_callbacks(self) -> list[_TwoPhaseCallbacks]:
        """Validate and bind callbacks before activation begins."""
        callbacks: list[_TwoPhaseCallbacks] = []
        invalid_agents: list[str] = []

        for agent in list(self.model.agents):
            if not self.model.agents._is_activation_eligible(agent):
                continue

            step_callback = getattr(agent, "step", None)
            advance_callback = getattr(agent, "advance", None)
            invalid_methods: list[str] = []

            if not callable(step_callback):
                invalid_methods.append("step")

            if not callable(advance_callback):
                invalid_methods.append("advance")

            if invalid_methods:
                method_list = ", ".join(f"{method_name}()" for method_name in invalid_methods)
                invalid_agents.append(
                    f"agent {agent.unique_id!r}: non-callable or missing {method_list}"
                )
                continue

            callbacks.append(
                (
                    agent,
                    cast(Callable[[], None], step_callback),
                    cast(Callable[[], None], advance_callback),
                )
            )

        if invalid_agents:
            details = "; ".join(invalid_agents)
            raise TypeError(f"{_CONTRACT_ERROR}; invalid agents: {details}")

        return callbacks
