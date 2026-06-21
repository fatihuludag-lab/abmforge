from __future__ import annotations

import importlib
import platform
import sys
import traceback
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml

from abmforge._version import __version__
from abmforge.core.model import Model
from abmforge.core.status import COMPLETED, CREATED, FAILED, STOPPED
from abmforge.data.dataset import Dataset
from abmforge.experiment.result import RunResult


def _import_model_class(import_path: str) -> type[Model]:
    """Import a model class from a dotted import path."""
    module_name, separator, class_name = import_path.rpartition(".")

    if not separator:
        raise ValueError(
            "Model path must be a dotted import path, "
            "for example 'examples.schelling.model.SchellingModel'"
        )

    module = importlib.import_module(module_name)
    model_cls = getattr(module, class_name)

    if not isinstance(model_cls, type) or not issubclass(model_cls, Model):
        raise TypeError(f"Imported object is not a Model subclass: {import_path}")

    return model_cls


@dataclass(slots=True)
class Scenario:
    """Configuration for one reproducible model run."""

    model: type[Model]
    parameters: dict[str, Any] = field(default_factory=dict)
    seed: int | None = None
    steps: int = 0
    stop_when: Callable[[Model], bool] | None = None
    name: str | None = None

    @classmethod
    def from_yaml(cls, path: str | Path) -> Scenario:
        """Create a scenario from a YAML configuration file."""
        scenario_path = Path(path)

        with scenario_path.open(encoding="utf-8") as file:
            config = yaml.safe_load(file)

        if config is None:
            raise ValueError("Scenario YAML document must be a mapping")

        if not isinstance(config, Mapping):
            raise ValueError("Scenario YAML document must be a mapping")

        model_path = config.get("model")
        if model_path is None:
            raise ValueError("Missing required field: model")

        if not isinstance(model_path, str) or not model_path:
            raise ValueError("Field 'model' must be a string")

        name = config.get("name")
        if name is not None and not isinstance(name, str):
            raise ValueError("Field 'name' must be a string or null")

        parameters = config.get("parameters", {})
        if parameters is None:
            parameters = {}

        if not isinstance(parameters, Mapping):
            raise ValueError("Field 'parameters' must be a mapping/object")

        run_config = config.get("run", {})
        if run_config is None:
            run_config = {}

        if not isinstance(run_config, Mapping):
            raise ValueError("Field 'run' must be a mapping/object")

        if "steps" not in run_config:
            raise ValueError("Missing required field: run.steps")

        seed = run_config.get("seed")
        steps = run_config["steps"]

        if seed is not None and (not isinstance(seed, int) or isinstance(seed, bool)):
            raise ValueError("Field 'run.seed' must be an integer or null")

        if not isinstance(steps, int) or isinstance(steps, bool):
            raise ValueError("Field 'run.steps' must be an integer")

        if steps < 0:
            raise ValueError("Field 'run.steps' must be non-negative")

        model_cls = _import_model_class(model_path)

        return cls(
            model=model_cls,
            parameters=dict(parameters),
            seed=seed,
            steps=steps,
            name=name,
        )

    def run(
        self,
        *,
        seed: int | None = None,
        raise_on_error: bool = True,
    ) -> RunResult:
        """Instantiate and run the scenario.

        Parameters
        ----------
        seed:
            Optional seed override.
        raise_on_error:
            When True, exceptions are re-raised after failure metadata is recorded.
            When False, a failed RunResult is returned instead.
        """
        run_seed = self.seed if seed is None else seed
        scenario_name = self.name or self.model.__name__
        started_at = datetime.now(timezone.utc).isoformat()

        try:
            model = self.model(parameters=self.parameters, seed=run_seed)
        except Exception as exc:
            result = self._failed_before_model_created(
                exc=exc,
                run_seed=run_seed,
                scenario_name=scenario_name,
                started_at=started_at,
                raise_on_error=raise_on_error,
            )
            if raise_on_error:
                raise
            return result

        model.record.dataset.add_run(
            run_id=model.run_id,
            scenario=scenario_name,
            model_name=self.model.__name__,
            parameters=dict(self.parameters),
            seed=run_seed,
            status="running",
            started_at=started_at,
            python_version=sys.version,
            platform=platform.platform(),
            abmforge_version=__version__,
        )

        try:
            model.setup()

            if self.steps < 0:
                raise ValueError("steps must be non-negative")

            for _ in range(self.steps):
                if model.status == STOPPED:
                    break
                if self.stop_when is not None and self.stop_when(model):
                    model.stop("stop_condition")
                    break

                model.run_for(1)
                if model.status == STOPPED:
                    break

                if self.stop_when is not None and self.stop_when(model):
                    model.stop("stop_condition")
                    break

        except Exception as exc:
            result = self._failed_after_model_created(
                model=model,
                exc=exc,
                scenario_name=scenario_name,
                raise_on_error=raise_on_error,
            )
            if raise_on_error:
                raise
            return result

        if model.status == CREATED:
            model.status = COMPLETED
        status = model.status
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

    def _failed_after_model_created(
        self,
        *,
        model: Model,
        exc: Exception,
        scenario_name: str,
        raise_on_error: bool,
    ) -> RunResult:
        exception_type = type(exc).__name__
        error_message = str(exc)
        error_repr = repr(exc)
        ended_at = datetime.now(timezone.utc).isoformat()

        model.status = FAILED
        model.record.dataset.record_error(
            step=model.steps,
            time=float(getattr(model, "time", 0.0)),
            exception_type=exception_type,
            message=error_message,
            component="Scenario.run",
            traceback_text=traceback.format_exc(),
            recoverable=not raise_on_error,
            details={
                "scenario": scenario_name,
                "model_name": self.model.__name__,
            },
        )
        model.record.dataset.update_last_run(
            status=FAILED,
            error=error_repr,
            error_message=error_message,
            exception_type=exception_type,
            ended_at=ended_at,
            steps=model.steps,
            stop_reason=model.stop_reason,
        )

        return RunResult(
            run_id=model.run_id,
            model=model,
            dataset=model.record.dataset,
            status=FAILED,
            steps=model.steps,
            stop_reason=model.stop_reason,
            error=error_repr,
            exception_type=exception_type,
        )

    def _failed_before_model_created(
        self,
        *,
        exc: Exception,
        run_seed: int | None,
        scenario_name: str,
        started_at: str,
        raise_on_error: bool,
    ) -> RunResult:
        exception_type = type(exc).__name__
        error_message = str(exc)
        error_repr = repr(exc)
        ended_at = datetime.now(timezone.utc).isoformat()
        run_id = f"failed-{uuid4().hex}"
        dataset = Dataset(run_id=run_id)

        dataset.add_run(
            run_id=run_id,
            scenario=scenario_name,
            model_name=self.model.__name__,
            parameters=dict(self.parameters),
            seed=run_seed,
            status=FAILED,
            started_at=started_at,
            ended_at=ended_at,
            python_version=sys.version,
            platform=platform.platform(),
            abmforge_version=__version__,
            error=error_repr,
            error_message=error_message,
            exception_type=exception_type,
            steps=0,
            stop_reason=None,
        )
        dataset.record_error(
            step=0,
            time=0.0,
            exception_type=exception_type,
            message=error_message,
            component="Scenario.construct",
            traceback_text=traceback.format_exc(),
            recoverable=not raise_on_error,
            details={
                "scenario": scenario_name,
                "model_name": self.model.__name__,
            },
        )

        return RunResult(
            run_id=run_id,
            model=None,
            dataset=dataset,
            status=FAILED,
            steps=0,
            stop_reason=None,
            error=error_repr,
            exception_type=exception_type,
        )
