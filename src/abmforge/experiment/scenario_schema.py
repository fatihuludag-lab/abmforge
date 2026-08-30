from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

SCENARIO_SCHEMA_VERSION = "abmforge.scenario.v1"

_ALLOWED_ROOT_FIELDS = frozenset(
    {
        "schema_version",
        "name",
        "model",
        "parameters",
        "run",
        "inputs",
        "extensions",
    }
)
_ALLOWED_RUN_FIELDS = frozenset({"seed", "steps", "stop"})
_ALLOWED_INPUT_FIELDS = frozenset({"root", "artifacts"})
_ALLOWED_STOP_FIELDS = frozenset({"field", "operator", "value"})
_SUPPORTED_STOP_OPERATORS = frozenset({"eq", "ne", "lt", "le", "gt", "ge"})


class ScenarioValidationError(ValueError):
    # Raised when a scenario YAML document fails validation.
    #
    # The message is intentionally human-readable because it is surfaced by the
    # command-line interface before a scenario run starts.

    def __init__(
        self,
        message: str,
        *,
        path: str | Path | None = None,
        field: str | None = None,
        hint: str | None = None,
    ) -> None:
        self.message = message
        self.path = Path(path) if path is not None else None
        self.field = field
        self.hint = hint

        details: list[str] = []
        if self.path is not None:
            details.append(f"file: {self.path}")
        if self.field is not None:
            details.append(f"field: {self.field}")

        formatted = message
        if details:
            formatted = f"{formatted} ({'; '.join(details)})"
        if hint:
            formatted = f"{formatted}. Hint: {hint}"

        super().__init__(formatted)


@dataclass(frozen=True, slots=True)
class StopConditionV1:
    """Declarative, serializable stop condition for Scenario Schema V1."""

    field: str
    operator: str
    value: Any

    def evaluate(self, model: Any) -> bool:
        """Evaluate the condition against one model instance."""
        try:
            observed = getattr(model, self.field)
        except AttributeError as exc:
            raise AttributeError(
                f"Declarative stop field {self.field!r} does not exist on "
                f"model {type(model).__name__!r}"
            ) from exc

        if self.operator == "eq":
            return bool(observed == self.value)
        if self.operator == "ne":
            return bool(observed != self.value)
        if self.operator == "lt":
            return bool(observed < self.value)
        if self.operator == "le":
            return bool(observed <= self.value)
        if self.operator == "gt":
            return bool(observed > self.value)
        if self.operator == "ge":
            return bool(observed >= self.value)

        raise RuntimeError(f"Unsupported validated stop operator: {self.operator}")


@dataclass(frozen=True, slots=True)
class ScenarioSchemaV1:
    """Validated, normalized representation of Scenario YAML v1."""

    model: str
    parameters: dict[str, Any]
    seed: int | None
    steps: int
    name: str | None
    extensions: dict[str, Any]
    stop: StopConditionV1 | None
    input_root: str | None = None
    input_artifacts: tuple[str, ...] = ()
    schema_version: str = SCENARIO_SCHEMA_VERSION

    @classmethod
    def from_mapping(
        cls,
        config: Any,
        *,
        path: str | Path | None = None,
    ) -> ScenarioSchemaV1:
        """Validate and normalize one Scenario YAML mapping."""
        if config is None or not isinstance(config, Mapping):
            raise ScenarioValidationError(
                "Scenario YAML document must be a mapping",
                path=path,
                hint=(
                    "Use a key-value YAML document with fields such as "
                    "'schema_version', 'model', and 'run'."
                ),
            )

        schema_version = config.get("schema_version")
        if schema_version is None:
            raise ScenarioValidationError(
                "Missing required field: schema_version",
                path=path,
                field="schema_version",
                hint=f"Set 'schema_version' to '{SCENARIO_SCHEMA_VERSION}'.",
            )

        if not isinstance(schema_version, str) or not schema_version:
            raise ScenarioValidationError(
                "Field 'schema_version' must be a string",
                path=path,
                field="schema_version",
                hint=f"Use '{SCENARIO_SCHEMA_VERSION}'.",
            )

        if schema_version != SCENARIO_SCHEMA_VERSION:
            raise ScenarioValidationError(
                f"Unsupported scenario schema version: {schema_version}",
                path=path,
                field="schema_version",
                hint=f"Supported version: '{SCENARIO_SCHEMA_VERSION}'.",
            )

        unknown_root = sorted(str(key) for key in config if key not in _ALLOWED_ROOT_FIELDS)
        if unknown_root:
            field = unknown_root[0]
            raise ScenarioValidationError(
                f"Unknown scenario field: {field}",
                path=path,
                field=field,
                hint=("Remove the field or place extension-specific data under 'extensions'."),
            )

        model_path = config.get("model")
        if model_path is None:
            raise ScenarioValidationError(
                "Missing required field: model",
                path=path,
                field="model",
                hint=("Set 'model' to a dotted import path such as 'model.model.MyModel'."),
            )

        if not isinstance(model_path, str) or not model_path:
            raise ScenarioValidationError(
                "Field 'model' must be a string",
                path=path,
                field="model",
                hint="Use a dotted Python import path string.",
            )

        name = config.get("name")
        if name is not None and not isinstance(name, str):
            raise ScenarioValidationError(
                "Field 'name' must be a string or null",
                path=path,
                field="name",
                hint="Use a YAML string or remove the field.",
            )

        parameters = config.get("parameters", {})
        if parameters is None:
            parameters = {}
        if not isinstance(parameters, Mapping):
            raise ScenarioValidationError(
                "Field 'parameters' must be a mapping/object",
                path=path,
                field="parameters",
                hint=("Use key-value pairs under 'parameters' or set it to null."),
            )

        run_config = config.get("run", {})
        if run_config is None:
            run_config = {}
        if not isinstance(run_config, Mapping):
            raise ScenarioValidationError(
                "Field 'run' must be a mapping/object",
                path=path,
                field="run",
                hint="Use a mapping with at least 'steps'.",
            )

        unknown_run = sorted(str(key) for key in run_config if key not in _ALLOWED_RUN_FIELDS)
        if unknown_run:
            field = f"run.{unknown_run[0]}"
            raise ScenarioValidationError(
                f"Unknown run field: {field}",
                path=path,
                field=field,
                hint="Supported run fields are 'seed', 'steps', and 'stop'.",
            )

        if "steps" not in run_config:
            raise ScenarioValidationError(
                "Missing required field: run.steps",
                path=path,
                field="run.steps",
                hint="Set a non-negative integer number of simulation steps.",
            )

        seed = run_config.get("seed")
        steps = run_config["steps"]

        if seed is not None and (not isinstance(seed, int) or isinstance(seed, bool)):
            raise ScenarioValidationError(
                "Field 'run.seed' must be an integer or null",
                path=path,
                field="run.seed",
                hint=("Use an integer seed for reproducibility or null for no explicit seed."),
            )

        if not isinstance(steps, int) or isinstance(steps, bool):
            raise ScenarioValidationError(
                "Field 'run.steps' must be an integer",
                path=path,
                field="run.steps",
                hint="Use an integer value such as 10.",
            )

        if steps < 0:
            raise ScenarioValidationError(
                "Field 'run.steps' must be non-negative",
                path=path,
                field="run.steps",
                hint="Use zero or a positive integer.",
            )

        stop: StopConditionV1 | None = None
        stop_config = run_config.get("stop")
        if stop_config is not None:
            if not isinstance(stop_config, Mapping):
                raise ScenarioValidationError(
                    "Field 'run.stop' must be a mapping/object",
                    path=path,
                    field="run.stop",
                    hint=("Use 'field', 'operator', and 'value' under 'run.stop'."),
                )

            unknown_stop = sorted(
                str(key) for key in stop_config if key not in _ALLOWED_STOP_FIELDS
            )
            if unknown_stop:
                field = f"run.stop.{unknown_stop[0]}"
                raise ScenarioValidationError(
                    f"Unknown stop field: {field}",
                    path=path,
                    field=field,
                    hint=("Supported stop fields are 'field', 'operator', and 'value'."),
                )

            for required in ("field", "operator", "value"):
                if required not in stop_config:
                    field = f"run.stop.{required}"
                    raise ScenarioValidationError(
                        f"Missing required field: {field}",
                        path=path,
                        field=field,
                    )

            stop_field = stop_config["field"]
            if (
                not isinstance(stop_field, str)
                or not stop_field
                or not stop_field.isidentifier()
                or stop_field.startswith("_")
            ):
                raise ScenarioValidationError(
                    ("Field 'run.stop.field' must be a public model attribute name"),
                    path=path,
                    field="run.stop.field",
                    hint=(
                        "Use a public Python identifier such as 'infected' "
                        "or 'steps'. Dotted and private names are not "
                        "supported in V1."
                    ),
                )

            stop_operator = stop_config["operator"]
            if not isinstance(stop_operator, str) or stop_operator not in _SUPPORTED_STOP_OPERATORS:
                raise ScenarioValidationError(
                    f"Unsupported stop operator: {stop_operator}",
                    path=path,
                    field="run.stop.operator",
                    hint=("Supported operators are eq, ne, lt, le, gt, and ge."),
                )

            stop_value = stop_config["value"]
            if isinstance(stop_value, (Mapping, list, tuple, set)):
                raise ScenarioValidationError(
                    "Field 'run.stop.value' must be a scalar value",
                    path=path,
                    field="run.stop.value",
                    hint="Use null, boolean, integer, float, or string.",
                )

            stop = StopConditionV1(
                field=stop_field,
                operator=stop_operator,
                value=stop_value,
            )

        input_root: str | None = None
        input_artifacts: tuple[str, ...] = ()

        if "inputs" in config:
            inputs = config["inputs"]

            if not isinstance(inputs, Mapping):
                raise ScenarioValidationError(
                    "Field 'inputs' must be a mapping/object",
                    path=path,
                    field="inputs",
                    hint=("Use 'root' and 'artifacts' under 'inputs'."),
                )

            unknown_inputs = sorted(str(key) for key in inputs if key not in _ALLOWED_INPUT_FIELDS)
            if unknown_inputs:
                field = f"inputs.{unknown_inputs[0]}"
                raise ScenarioValidationError(
                    f"Unknown inputs field: {field}",
                    path=path,
                    field=field,
                    hint=("Supported inputs fields are 'root' and 'artifacts'."),
                )

            root_value = inputs.get("root", ".")

            if not isinstance(root_value, str) or not root_value:
                raise ScenarioValidationError(
                    "Field 'inputs.root' must be a non-empty string",
                    path=path,
                    field="inputs.root",
                    hint=("Use a portable relative path such as '.' or '..'."),
                )

            if "\\" in root_value or ":" in root_value:
                raise ScenarioValidationError(
                    "Field 'inputs.root' must use a portable relative path",
                    path=path,
                    field="inputs.root",
                    hint=("Use forward slashes and do not use drive-qualified or absolute paths."),
                )

            portable_root = PurePosixPath(root_value)

            if portable_root.is_absolute():
                raise ScenarioValidationError(
                    "Field 'inputs.root' must be relative",
                    path=path,
                    field="inputs.root",
                    hint=("Resolve the input root relative to the scenario YAML file."),
                )

            input_root = portable_root.as_posix()

            artifact_values = inputs.get("artifacts", [])

            if not isinstance(artifact_values, list):
                raise ScenarioValidationError(
                    "Field 'inputs.artifacts' must be a list",
                    path=path,
                    field="inputs.artifacts",
                    hint=("List portable file paths relative to inputs.root."),
                )

            normalized_artifacts: list[str] = []
            seen_artifacts: set[str] = set()

            for index, artifact_value in enumerate(artifact_values):
                field = f"inputs.artifacts[{index}]"

                if not isinstance(artifact_value, str) or not artifact_value:
                    raise ScenarioValidationError(
                        f"Field '{field}' must be a non-empty string",
                        path=path,
                        field=field,
                    )

                if "\\" in artifact_value or ":" in artifact_value:
                    raise ScenarioValidationError(
                        f"Field '{field}' must use a portable relative path",
                        path=path,
                        field=field,
                        hint=("Use forward slashes and paths relative to inputs.root."),
                    )

                portable_artifact = PurePosixPath(artifact_value)

                if (
                    portable_artifact.is_absolute()
                    or ".." in portable_artifact.parts
                    or portable_artifact.as_posix() in {".", ".."}
                ):
                    raise ScenarioValidationError(
                        f"Field '{field}' must remain inside inputs.root",
                        path=path,
                        field=field,
                        hint=("Use a relative file path without '..'."),
                    )

                normalized = portable_artifact.as_posix()

                if normalized in seen_artifacts:
                    raise ScenarioValidationError(
                        f"Duplicate declared input path: {normalized}",
                        path=path,
                        field=field,
                    )

                seen_artifacts.add(normalized)
                normalized_artifacts.append(normalized)

            input_artifacts = tuple(normalized_artifacts)

        extensions = config.get("extensions", {})
        if extensions is None:
            extensions = {}
        if not isinstance(extensions, Mapping):
            raise ScenarioValidationError(
                "Field 'extensions' must be a mapping/object",
                path=path,
                field="extensions",
                hint=("Use namespaced key-value mappings under 'extensions' or remove the field."),
            )

        return cls(
            model=model_path,
            parameters=dict(parameters),
            seed=seed,
            steps=steps,
            name=name,
            extensions=dict(extensions),
            stop=stop,
            input_root=input_root,
            input_artifacts=input_artifacts,
        )
