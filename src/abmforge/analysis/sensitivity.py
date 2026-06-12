from __future__ import annotations

from collections import defaultdict
from typing import Any


class SensitivityAnalysis:
    """Simple sensitivity analysis for ABMForge experiment results.

    This MVP estimates parameter sensitivity by comparing the mean final metric
    value across different parameter values.
    """

    def __init__(
        self,
        experiment_result: Any,
        *,
        metric: str,
    ) -> None:
        self.experiment_result = experiment_result
        self.metric = metric

    def final_metric_by_run(self) -> dict[str, float]:
        """Return the final metric value for each run."""
        values: dict[str, float] = {}

        for run in self.experiment_result:
            records = [
                record
                for record in run.dataset.model_records
                if record.get("metric") == self.metric
            ]

            if not records:
                continue

            final_record = max(records, key=lambda record: record["step"])
            values[run.run_id] = float(final_record["value"])

        return values

    def parameter_effects(self) -> dict[str, dict[str, float]]:
        """Estimate simple parameter effects on the selected metric.

        For each parameter, this returns the mean final metric for every
        observed parameter value.
        """
        run_values = self.final_metric_by_run()
        grouped: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

        for run in self.experiment_result:
            if run.run_id not in run_values:
                continue

            if not run.dataset.runs:
                continue

            parameters = run.dataset.runs[0].get("parameters", {})
            if not isinstance(parameters, dict):
                continue

            for parameter_name, parameter_value in parameters.items():
                grouped[parameter_name][str(parameter_value)].append(run_values[run.run_id])

        effects: dict[str, dict[str, float]] = {}

        for parameter_name, value_groups in grouped.items():
            effects[parameter_name] = {}
            for parameter_value, values in value_groups.items():
                effects[parameter_name][parameter_value] = sum(values) / len(values)

        return effects

    def rank(self) -> list[dict[str, float | str]]:
        """Rank parameters by range of mean final metric values."""
        effects = self.parameter_effects()
        ranking: list[dict[str, float | str]] = []

        for parameter_name, value_effects in effects.items():
            values = list(value_effects.values())
            if not values:
                continue

            sensitivity = max(values) - min(values)

            ranking.append(
                {
                    "parameter": parameter_name,
                    "sensitivity": sensitivity,
                    "min_mean": min(values),
                    "max_mean": max(values),
                }
            )

        return sorted(
            ranking,
            key=lambda item: float(item["sensitivity"]),
            reverse=True,
        )

    def summary(self) -> dict[str, Any]:
        """Return a compact sensitivity summary."""
        return {
            "metric": self.metric,
            "effects": self.parameter_effects(),
            "ranking": self.rank(),
        }
