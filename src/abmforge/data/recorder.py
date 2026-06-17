from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from abmforge.data.storage.inmemory import InMemoryStorage

if TYPE_CHECKING:
    from abmforge.core.model import Model


class Recorder:
    """Collect model-level and agent-level records into a Dataset."""

    def __init__(self, model: Model) -> None:
        self.model = model
        self.dataset = InMemoryStorage(run_id=model.run_id)
        self._metrics: list[tuple[str, Callable[[Model], Any]]] = []
        self._agent_variables: list[str] = []

    def metric(self, name: str, function: Callable[[Model], Any]) -> None:
        """Register a model-level metric."""
        self._metrics.append((name, function))

    def agent(self, variable: str) -> None:
        """Register an agent attribute to record after every step."""
        self._agent_variables.append(variable)

    def collect(self) -> None:
        """Collect registered metrics and agent attributes."""
        for name, function in self._metrics:
            value = function(self.model)
            self.dataset.record_model(
                step=self.model.steps,
                time=self.model.time,
                metric=name,
                value=value,
            )

        for variable in self._agent_variables:
            for agent in self.model.agents:
                if hasattr(agent, variable):
                    self.dataset.record_agent(
                        step=self.model.steps,
                        time=self.model.time,
                        agent_id=agent.unique_id,
                        agent_type=type(agent).__name__,
                        variable=variable,
                        value=getattr(agent, variable),
                    )

    def event(
        self,
        *,
        event_id: int | str,
        owner: int | str | None,
        tags: list[str],
        status: str,
    ) -> None:
        """Record an event queue transition."""
        self.dataset.record_event(
            step=self.model.steps,
            time=self.model.time,
            event_id=event_id,
            owner=owner,
            tags=tags,
            status=status,
        )

    def lifecycle(
        self,
        event: str,
        *,
        agent_id: int | str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record a lifecycle transition."""
        self.dataset.record_lifecycle(
            step=self.model.steps,
            time=self.model.time,
            event=event,
            agent_id=agent_id,
            details=details,
        )
