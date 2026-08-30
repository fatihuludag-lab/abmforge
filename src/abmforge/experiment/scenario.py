from __future__ import annotations

import importlib
import platform
import sys
import traceback
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml

from abmforge._version import __version__
from abmforge.core.model import Model
from abmforge.core.status import COMPLETED, CREATED, FAILED, RUNNING, STOPPED
from abmforge.data.dataset import Dataset
from abmforge.experiment.result import RunResult
from abmforge.experiment.run_index import RUN_IDENTITY_SCHEMA_VERSION
from abmforge.experiment.scenario_schema import (
    ScenarioSchemaV1,
    ScenarioValidationError,
    StopConditionV1,
)
from abmforge.repro.execution_fingerprint import (
    ExecutionFingerprintV3,
    runtime_framework_execution_identity,
)
from abmforge.repro.input_provenance import DeclaredInputIdentityV1


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
    input_artifacts: Sequence[str | Path] = field(default_factory=tuple)
    input_root: str | Path | None = None
    schema_version: str | None = None
    extensions: dict[str, Any] = field(default_factory=dict)
    stop_condition: StopConditionV1 | None = None

    def __post_init__(self) -> None:
        if self.stop_when is not None and self.stop_condition is not None:
            raise ValueError("Scenario cannot define both stop_when and stop_condition")

    @classmethod
    def from_yaml(cls, path: str | Path) -> Scenario:
        """Create a scenario from a YAML configuration file."""
        scenario_path = Path(path)

        try:
            with scenario_path.open(encoding="utf-8") as file:
                config = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            raise ScenarioValidationError(
                "Scenario YAML could not be parsed",
                path=scenario_path,
                hint=str(exc),
            ) from exc

        if config is None:
            raise ScenarioValidationError(
                "Scenario YAML document must be a mapping",
                path=scenario_path,
                hint="Use a key-value YAML document with fields such as 'model' and 'run'.",
            )

        if not isinstance(config, Mapping):
            raise ScenarioValidationError(
                "Scenario YAML document must be a mapping",
                path=scenario_path,
                hint="Use a key-value YAML document with fields such as 'model' and 'run'.",
            )

        schema = ScenarioSchemaV1.from_mapping(
            config,
            path=scenario_path,
        )

        try:
            model_cls = _import_model_class(schema.model)
        except (ImportError, AttributeError, TypeError, ValueError) as exc:
            raise ScenarioValidationError(
                str(exc),
                path=scenario_path,
                field="model",
                hint=(
                    "Check that the dotted Python path is importable from the "
                    "current working directory or installed package."
                ),
            ) from exc

        resolved_input_root: Path | None = None
        resolved_input_artifacts: tuple[Path, ...] = ()

        if schema.input_root is not None:
            resolved_input_root = (scenario_path.parent / Path(schema.input_root)).resolve()

            resolved_input_artifacts = tuple(
                (resolved_input_root / Path(input_path)).resolve()
                for input_path in schema.input_artifacts
            )

        return cls(
            model=model_cls,
            parameters=dict(schema.parameters),
            seed=schema.seed,
            steps=schema.steps,
            name=schema.name,
            input_artifacts=resolved_input_artifacts,
            input_root=resolved_input_root,
            schema_version=schema.schema_version,
            extensions=dict(schema.extensions),
            stop_condition=schema.stop,
        )

    def declared_input_identity(self) -> DeclaredInputIdentityV1:
        """Return the current identity of explicitly declared input files."""
        return DeclaredInputIdentityV1.from_paths(
            self.input_artifacts,
            root=self.input_root,
        )

    def execution_fingerprint(
        self,
        *,
        seed: int | None = None,
    ) -> ExecutionFingerprintV3:
        """Return the input- and framework-aware identity for this execution."""
        run_seed = self.seed if seed is None else seed
        framework = runtime_framework_execution_identity()
        declared_inputs = self.declared_input_identity()

        return ExecutionFingerprintV3.create(
            model=self.model,
            scenario=self.name or self.model.__name__,
            seed=run_seed,
            steps=self.steps,
            parameters=self.parameters,
            framework_version=framework.version,
            framework_package_tree_sha256=framework.package_tree_sha256,
            declared_inputs=declared_inputs,
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
        execution_fingerprint = self.execution_fingerprint(seed=run_seed).to_dict()
        started_at = datetime.now(timezone.utc).isoformat()

        try:
            model = self.model(parameters=self.parameters, seed=run_seed)
        except Exception as exc:
            result = self._failed_before_model_created(
                exc=exc,
                run_seed=run_seed,
                scenario_name=scenario_name,
                started_at=started_at,
                execution_fingerprint=execution_fingerprint,
                raise_on_error=raise_on_error,
            )
            if raise_on_error:
                raise
            return result

        model.record.dataset.add_run(
            run_id=model.run_id,
            scenario=scenario_name,
            model_name=self.model.__name__,
            model_module=self.model.__module__,
            model_qualname=self.model.__qualname__,
            run_identity_version=RUN_IDENTITY_SCHEMA_VERSION,
            execution_fingerprint=execution_fingerprint,
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

            if model.status != STOPPED:
                model.running = True
                model.status = RUNNING

            for _ in range(self.steps):
                if model.status == STOPPED:
                    break
                if self._stop_requested(model):
                    model.stop("stop_condition")
                    break

                model._run_for(1, finalize=False)
                if model.status == STOPPED:
                    break

                if self._stop_requested(model):
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

        if model.status in {CREATED, RUNNING}:
            model.running = False
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

    def _stop_requested(self, model: Model) -> bool:
        if self.stop_condition is not None:
            return self.stop_condition.evaluate(model)
        if self.stop_when is not None:
            return bool(self.stop_when(model))
        return False

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

        model.running = False
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
            _exception=exc,
        )

    def _failed_before_model_created(
        self,
        *,
        exc: Exception,
        run_seed: int | None,
        scenario_name: str,
        started_at: str,
        execution_fingerprint: dict[str, Any],
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
            model_module=self.model.__module__,
            model_qualname=self.model.__qualname__,
            run_identity_version=RUN_IDENTITY_SCHEMA_VERSION,
            execution_fingerprint=execution_fingerprint,
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
            _exception=exc,
        )
