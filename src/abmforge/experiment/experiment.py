from __future__ import annotations

from dataclasses import dataclass

from abmforge.experiment.result import RunResult
from abmforge.experiment.scenario import Scenario


@dataclass(slots=True)
class ExperimentResult:
    """Result of running multiple scenarios."""

    results: list[RunResult]

    @property
    def run_count(self) -> int:
        return len(self.results)

    @property
    def failed_count(self) -> int:
        return sum(1 for result in self.results if result.status == "failed")


class Experiment:
    """Minimal local experiment runner."""

    def __init__(self, scenarios: list[Scenario]) -> None:
        self.scenarios = scenarios

    def run(self) -> ExperimentResult:
        """Run scenarios sequentially."""
        return ExperimentResult(results=[scenario.run() for scenario in self.scenarios])
