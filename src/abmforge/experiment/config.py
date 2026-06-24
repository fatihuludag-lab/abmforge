from __future__ import annotations

import importlib
import json
import random
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

from abmforge.core.model import Model
from abmforge.experiment.experiment import Experiment, ExperimentResult


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    """Validated configuration for a multi-run ABMForge experiment."""

    name: str | None
    model: type[Model]
    model_path: str
    base_parameters: dict[str, Any]
    parameters: dict[str, list[Any]]
    seeds: list[int]
    steps: int
    primary_metric: str | None = None

    @classmethod
    def from_yaml(cls, path: str | Path) -> ExperimentConfig:
        """Load and validate an experiment YAML file."""

        config_path = Path(path)
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))

        if raw is None:
            raise ValueError("Experiment YAML is empty")

        root = _require_mapping(raw, "root")

        name = root.get("name")
        if name is not None and not isinstance(name, str):
            raise ValueError("'name' must be a string when provided")

        model_path = _require_string(root.get("model"), "model")
        model = _import_model_class(model_path)

        base_parameters = _optional_mapping(
            root.get("base_parameters", {}),
            "base_parameters",
        )

        experiment_section = _require_mapping(
            root.get("experiment"),
            "experiment",
        )
        parameters = _require_parameter_grid(
            experiment_section.get("parameters"),
            "experiment.parameters",
        )
        _validate_no_parameter_overlap(base_parameters, parameters)

        seeds = _parse_seeds(
            experiment_section.get("seeds"),
            "experiment.seeds",
        )

        run_section = _require_mapping(root.get("run"), "run")
        steps = _require_positive_int(run_section.get("steps"), "run.steps")

        outputs_section = root.get("outputs", {})
        outputs = _optional_mapping(outputs_section, "outputs")
        primary_metric = outputs.get("primary_metric")

        if primary_metric is not None and not isinstance(primary_metric, str):
            raise ValueError("'outputs.primary_metric' must be a string")

        return cls(
            name=name,
            model=model,
            model_path=model_path,
            base_parameters=base_parameters,
            parameters=parameters,
            seeds=seeds,
            steps=steps,
            primary_metric=primary_metric,
        )

    def experiment_parameters(self) -> dict[str, list[Any]]:
        """Return fixed and swept parameters in Experiment-compatible form."""

        fixed = {name: [value] for name, value in self.base_parameters.items()}
        return fixed | self.parameters

    def to_experiment(self, *, continue_on_error: bool = False) -> Experiment:
        """Build an Experiment instance from the validated config."""

        seeds: list[int | None] = list(self.seeds)

        return Experiment(
            model=self.model,
            parameters=self.experiment_parameters(),
            seeds=seeds,
            steps=self.steps,
            name=self.name,
            continue_on_error=continue_on_error,
        )


def write_experiment_outputs(
    result: ExperimentResult,
    config: ExperimentConfig,
    config_path: str | Path,
    output_dir: str | Path,
    *,
    overwrite: bool = False,
) -> Path:
    """Write a lightweight multi-run experiment output directory."""

    target = Path(output_dir)

    if target.exists() and any(target.iterdir()):
        if not overwrite:
            raise FileExistsError(
                "Experiment output directory already exists and is not empty: "
                f"{target}. Use --overwrite to replace it."
            )
        shutil.rmtree(target)

    configs_dir = target / "configs"
    data_dir = target / "data"
    reports_dir = target / "reports"

    configs_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(config_path, configs_dir / "experiment.yaml")
    result.write_csv(data_dir)

    summary = {
        "name": config.name,
        "model": config.model_path,
        "steps": config.steps,
        "seed_count": len(config.seeds),
        "run_count_expected": _expected_run_count(config),
        "base_parameters": config.base_parameters,
        "parameters": config.parameters,
        "primary_metric": config.primary_metric,
        "result_summary": _safe_summary(result),
    }

    summary_path = reports_dir / "experiment_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, default=str),
        encoding="utf-8",
    )

    readme_path = reports_dir / "README_RESULTS.md"
    readme_path.write_text(
        _format_results_readme(config, summary_path),
        encoding="utf-8",
    )

    return target


def _import_model_class(path: str) -> type[Model]:
    module_name, separator, class_name = path.rpartition(".")

    if not separator:
        raise ValueError(
            "'model' must be a fully qualified import path, for example 'model.model.MyModel'"
        )

    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise ValueError(f"Could not import model module {module_name!r}") from exc

    try:
        candidate = getattr(module, class_name)
    except AttributeError as exc:
        raise ValueError(
            f"Model class {class_name!r} was not found in module {module_name!r}"
        ) from exc

    if not isinstance(candidate, type) or not issubclass(candidate, Model):
        raise ValueError(f"Configured model {path!r} must be a subclass of abmforge.Model")

    return cast(type[Model], candidate)


def _parse_seeds(value: Any, name: str) -> list[int]:
    if isinstance(value, list):
        seeds = [int(seed) for seed in value]
    else:
        mapping = _require_mapping(value, name)
        count = _require_positive_int(mapping.get("count"), f"{name}.count")
        master_seed = _require_non_negative_int(
            mapping.get("master_seed"),
            f"{name}.master_seed",
        )
        rng = random.Random(master_seed)
        seeds = [rng.randrange(0, 2**32) for _ in range(count)]

    if not seeds:
        raise ValueError(f"'{name}' must contain at least one seed")

    for seed in seeds:
        if seed < 0:
            raise ValueError(f"'{name}' cannot contain negative seeds")

    return seeds


def _require_parameter_grid(value: Any, name: str) -> dict[str, list[Any]]:
    mapping = _require_mapping(value, name)

    if not mapping:
        raise ValueError(f"'{name}' must define at least one parameter")

    parameters: dict[str, list[Any]] = {}

    for parameter_name, values in mapping.items():
        if not isinstance(parameter_name, str):
            raise ValueError(f"'{name}' parameter names must be strings")

        if not isinstance(values, list):
            raise ValueError(f"'{name}.{parameter_name}' must be a list of values")

        if not values:
            raise ValueError(f"'{name}.{parameter_name}' must contain at least one value")

        parameters[parameter_name] = values

    return parameters


def _validate_no_parameter_overlap(
    base_parameters: dict[str, Any],
    parameters: dict[str, list[Any]],
) -> None:
    overlap = sorted(set(base_parameters) & set(parameters))

    if overlap:
        joined = ", ".join(overlap)
        raise ValueError(
            "Parameters cannot appear in both 'base_parameters' and "
            f"'experiment.parameters': {joined}"
        )


def _optional_mapping(value: Any, name: str) -> dict[str, Any]:
    if value is None:
        return {}

    return _require_mapping(value, name)


def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"'{name}' must be a mapping")

    return dict(value)


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{name}' must be a non-empty string")

    return value


def _require_positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"'{name}' must be a positive integer")

    if value <= 0:
        raise ValueError(f"'{name}' must be positive")

    return value


def _require_non_negative_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"'{name}' must be a non-negative integer")

    if value < 0:
        raise ValueError(f"'{name}' must be non-negative")

    return value


def _expected_run_count(config: ExperimentConfig) -> int:
    count = len(config.seeds)

    for values in config.experiment_parameters().values():
        count *= len(values)

    return count


def _safe_summary(result: ExperimentResult) -> Any:
    try:
        return result.summary()
    except Exception as exc:  # pragma: no cover - defensive reporting fallback
        return {"summary_error": str(exc)}


def _format_results_readme(config: ExperimentConfig, summary_path: Path) -> str:
    primary_metric = config.primary_metric or "not specified"

    return (
        "# ABMForge experiment results\n\n"
        f"- Experiment: {config.name or 'unnamed'}\n"
        f"- Model: `{config.model_path}`\n"
        f"- Steps per run: {config.steps}\n"
        f"- Seed count: {len(config.seeds)}\n"
        f"- Expected run count: {_expected_run_count(config)}\n"
        f"- Primary metric: `{primary_metric}`\n\n"
        "Generated files:\n\n"
        "- `configs/experiment.yaml`: copied source experiment configuration\n"
        "- `data/`: combined CSV tables written from `ExperimentResult`\n"
        f"- `{summary_path.name}`: machine-readable experiment summary\n"
    )
