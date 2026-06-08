from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from abmforge.core.model import Model
from abmforge.experiment.result import RunResult


@dataclass(slots=True)
class Scenario:
    """Configuration for one reproducible model run."""

    model: type[Model]
    parameters: dict[str, Any] = field(default_factory=dict)
    seed: int | None = None
    steps: int = 0
    stop_when: Callable[[Model], bool] | None = None
    name: str | None = None

    def run(self, *, seed: int | None = None) -> RunResult:
        """Instantiate and run the scenario."""
        run_seed = self.seed if seed is None else seed
        model = self.model(parameters=self.parameters, seed=run_seed)
        scenario_name = self.name or self.model.__name__

        started_at = datetime.now(timezone.utc).isoformat()
        model.record.dataset.add_run(
            run_id=model.run_id,
            scenario=scenario_name,
            model_name=self.model.__name__,
            parameters=dict(self.parameters),
            seed=run_seed,
            status="running",
            started_at=started_at,
        )

        try:
            model.setup()
            if self.steps < 0:
                raise ValueError("steps must be non-negative")

            for _ in range(self.steps):
                if self.stop_when is not None and self.stop_when(model):
                    model.stop("stop_condition")
                    break
                model.run_for(1)
                if self.stop_when is not None and self.stop_when(model):
                    model.stop("stop_condition")
                    break
        except Exception as exc:
            model.status = "failed"
            model.record.dataset.update_last_run(
                status="failed",
                error=repr(exc),
                ended_at=datetime.now(timezone.utc).isoformat(),
                steps=model.steps,
                stop_reason=model.stop_reason,
            )
            raise

        status = model.status if model.status != "created" else "completed"
        model.record.dataset.update_last_run(
            status=status,
            ended_at=datetime.now(timezone.utc).isoformat(),
            steps=model.steps,
            stop_reason=model.stop_reason,
        )
        return RunResult(
            run_id=model.run_id,
            model=model,
            dataset=model.record.dataset,
            status=status,
            steps=model.steps,
            stop_reason=model.stop_reason,
        )
