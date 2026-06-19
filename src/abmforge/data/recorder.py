from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from abmforge.data.storage.inmemory import InMemoryStorage

if TYPE_CHECKING:
    from abmforge.core.model import Model


ModelMetric = Callable[["Model"], Any]
ModelPredicate = Callable[["Model"], bool]
AgentPredicate = Callable[[Any], bool]


@dataclass(frozen=True, slots=True)
class _MetricRecordingOptions:
    every: int = 1
    when: ModelPredicate | None = None


@dataclass(frozen=True, slots=True)
class _AgentRecordingOptions:
    every: int = 1
    when: ModelPredicate | None = None
    where: AgentPredicate | None = None


def _validate_every(every: int) -> int:
    if not isinstance(every, int) or isinstance(every, bool) or every <= 0:
        raise ValueError("every must be a positive integer")

    return every


class Recorder:
    """Collect model-level and agent-level records into a Dataset."""

    def __init__(self, model: Model) -> None:
        self.model = model
        self.dataset = InMemoryStorage(run_id=model.run_id)
        self._metrics: list[tuple[str, ModelMetric]] = []
        self._metric_options: list[_MetricRecordingOptions] = []
        self._agent_variables: list[str] = []
        self._agent_options: list[_AgentRecordingOptions] = []

    def metric(
        self,
        name: str,
        function: ModelMetric,
        *,
        every: int = 1,
        when: ModelPredicate | None = None,
    ) -> None:
        """Register a model-level metric."""
        every = _validate_every(every)

        self._metrics.append((name, function))
        self._metric_options.append(
            _MetricRecordingOptions(
                every=every,
                when=when,
            )
        )

    def agent(
        self,
        variable: str,
        *,
        every: int = 1,
        when: ModelPredicate | None = None,
        where: AgentPredicate | None = None,
    ) -> None:
        """Register an agent attribute to record."""
        every = _validate_every(every)

        self._agent_variables.append(variable)
        self._agent_options.append(
            _AgentRecordingOptions(
                every=every,
                when=when,
                where=where,
            )
        )

    def collect(self) -> None:
        """Collect registered metrics and agent attributes."""
        for index, (name, function) in enumerate(self._metrics):
            metric_options = self._metric_options[index]

            if not self._should_record(metric_options.every, metric_options.when):
                continue

            value = function(self.model)
            self.dataset.record_model(
                step=self.model.steps,
                time=self.model.time,
                metric=name,
                value=value,
            )

        for index, variable in enumerate(self._agent_variables):
            agent_options = self._agent_options[index]

            if not self._should_record(agent_options.every, agent_options.when):
                continue

            for agent in self.model.agents:
                if agent_options.where is not None and not agent_options.where(agent):
                    continue

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

    def _should_record(
        self,
        every: int,
        when: ModelPredicate | None,
    ) -> bool:
        if self.model.steps % every != 0:
            return False

        return not (when is not None and not when(self.model))
