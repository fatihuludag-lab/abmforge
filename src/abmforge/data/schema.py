from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from abmforge.core.status import VALID_MODEL_STATUSES
from abmforge.time.status import VALID_EVENT_STATUSES

DATASET_SCHEMA_VERSION = "abmforge.dataset.v1"


class SchemaValidationError(ValueError):
    """Raised when dataset records do not satisfy a dataset schema."""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = list(errors)
        message = "Dataset schema validation failed:\n" + "\n".join(
            f"- {error}" for error in self.errors
        )
        super().__init__(message)


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_identifier(value: Any) -> bool:
    return isinstance(value, (str, int)) and not isinstance(value, bool)


def _matches_kind(value: Any, kind: str) -> bool:
    if kind == "any":
        return True

    if kind == "string":
        return isinstance(value, str)

    if kind == "integer":
        return _is_integer(value)

    if kind == "number":
        return _is_number(value)

    if kind == "boolean":
        return isinstance(value, bool)

    if kind == "object":
        return isinstance(value, dict)

    if kind == "array":
        return isinstance(value, list)

    if kind == "identifier":
        return _is_identifier(value)

    raise ValueError(f"Unsupported schema field kind: {kind}")


@dataclass(frozen=True, slots=True)
class FieldSpec:
    """Specification for one dataset table field."""

    name: str
    kind: str = "any"
    required: bool = True
    nullable: bool = False
    description: str = ""
    enum: tuple[Any, ...] | None = None

    def validate(self, record: Mapping[str, Any], *, path: str) -> list[str]:
        """Validate this field against one record."""
        errors: list[str] = []

        if self.name not in record:
            if self.required:
                errors.append(f"{path}.{self.name}: missing required field")
            return errors

        value = record[self.name]

        if value is None:
            if not self.nullable:
                errors.append(f"{path}.{self.name}: must not be null")
            return errors

        if self.enum is not None and value not in self.enum:
            allowed = ", ".join(str(item) for item in self.enum)
            errors.append(f"{path}.{self.name}: expected one of {{{allowed}}}, got {value!r}")
            return errors

        if not _matches_kind(value, self.kind):
            errors.append(f"{path}.{self.name}: expected {self.kind}, got {type(value).__name__}")

        return errors

    def to_dict(self) -> dict[str, Any]:
        """Return this field spec as a JSON-serializable dictionary."""
        data: dict[str, Any] = {
            "name": self.name,
            "kind": self.kind,
            "required": self.required,
            "nullable": self.nullable,
            "description": self.description,
        }

        if self.enum is not None:
            data["enum"] = list(self.enum)

        return data


@dataclass(frozen=True, slots=True)
class TableSchema:
    """Specification for one dataset table."""

    name: str
    fields: tuple[FieldSpec, ...]
    allow_extra_fields: bool = True
    description: str = ""

    def validate_records(self, records: Sequence[Any]) -> list[str]:
        """Validate all records in this table."""
        errors: list[str] = []
        expected_fields = {field.name for field in self.fields}

        for index, record in enumerate(records):
            path = f"{self.name}[{index}]"

            if not isinstance(record, Mapping):
                errors.append(f"{path}: expected object record, got {type(record).__name__}")
                continue

            for field in self.fields:
                errors.extend(field.validate(record, path=path))

            if not self.allow_extra_fields:
                extra_fields = sorted(set(record) - expected_fields)
                for field_name in extra_fields:
                    errors.append(f"{path}.{field_name}: unexpected field")

        return errors

    def to_dict(self) -> dict[str, Any]:
        """Return this table schema as a JSON-serializable dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "allow_extra_fields": self.allow_extra_fields,
            "fields": [field.to_dict() for field in self.fields],
        }


class DatasetSchemaV1:
    """Schema and validation utilities for ABMForge Dataset V1 tables."""

    version: ClassVar[str] = DATASET_SCHEMA_VERSION

    tables: ClassVar[dict[str, TableSchema]] = {
        "runs": TableSchema(
            name="runs",
            description="Run-level metadata records.",
            fields=(
                FieldSpec("run_id", "string", description="Unique run identifier."),
                FieldSpec("scenario", "string", required=False, nullable=True),
                FieldSpec("model_name", "string", required=False, nullable=True),
                FieldSpec("parameters", "object", required=False, nullable=True),
                FieldSpec("seed", "integer", required=False, nullable=True),
                FieldSpec(
                    "status",
                    "string",
                    required=False,
                    nullable=True,
                    enum=tuple(sorted(VALID_MODEL_STATUSES)),
                ),
                FieldSpec("started_at", "string", required=False, nullable=True),
                FieldSpec("ended_at", "string", required=False, nullable=True),
                FieldSpec("python_version", "string", required=False, nullable=True),
                FieldSpec("platform", "string", required=False, nullable=True),
                FieldSpec("abmforge_version", "string", required=False, nullable=True),
                FieldSpec("steps", "integer", required=False, nullable=True),
                FieldSpec("stop_reason", "string", required=False, nullable=True),
                FieldSpec("error", "string", required=False, nullable=True),
                FieldSpec("error_message", "string", required=False, nullable=True),
                FieldSpec("exception_type", "string", required=False, nullable=True),
            ),
        ),
        "model_records": TableSchema(
            name="model_records",
            description="Model-level time series records.",
            fields=(
                FieldSpec("run_id", "string"),
                FieldSpec("step", "integer"),
                FieldSpec("time", "number"),
                FieldSpec("metric", "string"),
                FieldSpec("value", "any"),
            ),
        ),
        "agent_records": TableSchema(
            name="agent_records",
            description="Agent-level variable records.",
            fields=(
                FieldSpec("run_id", "string"),
                FieldSpec("step", "integer"),
                FieldSpec("time", "number"),
                FieldSpec("agent_id", "identifier"),
                FieldSpec("agent_type", "string"),
                FieldSpec("variable", "string"),
                FieldSpec("value", "any"),
            ),
        ),
        "event_records": TableSchema(
            name="event_records",
            description="Event-level records.",
            fields=(
                FieldSpec("run_id", "string"),
                FieldSpec("step", "integer"),
                FieldSpec("time", "number"),
                FieldSpec("event_id", "identifier"),
                FieldSpec("owner", "identifier", nullable=True),
                FieldSpec("tags", "array"),
                FieldSpec(
                    "status",
                    "string",
                    enum=tuple(sorted(VALID_EVENT_STATUSES)),
                ),
            ),
        ),
        "lifecycle_records": TableSchema(
            name="lifecycle_records",
            description="Agent and model lifecycle transition records.",
            fields=(
                FieldSpec("run_id", "string"),
                FieldSpec("step", "integer"),
                FieldSpec("time", "number"),
                FieldSpec("event", "string"),
                FieldSpec("agent_id", "identifier", nullable=True),
                FieldSpec("details", "object"),
            ),
        ),
        "errors": TableSchema(
            name="errors",
            description="Error records produced by failed or recoverable runs.",
            fields=(
                FieldSpec("error_id", "string"),
                FieldSpec("run_id", "string"),
                FieldSpec("step", "integer"),
                FieldSpec("time", "number"),
                FieldSpec("component", "string", nullable=True),
                FieldSpec("exception_type", "string"),
                FieldSpec("message", "string"),
                FieldSpec("traceback", "string", nullable=True),
                FieldSpec("recoverable", "boolean"),
                FieldSpec("event_id", "identifier", nullable=True),
                FieldSpec("agent_id", "identifier", nullable=True),
                FieldSpec("details", "object"),
            ),
        ),
    }

    @classmethod
    def table_names(cls) -> tuple[str, ...]:
        """Return dataset table names in schema order."""
        return tuple(cls.tables)

    @classmethod
    def validate_dataset(
        cls,
        dataset: Any,
        *,
        raise_on_error: bool = True,
    ) -> list[str]:
        """Validate all known dataset tables.

        Parameters
        ----------
        dataset:
            Dataset-like object with table attributes.
        raise_on_error:
            When True, raise SchemaValidationError if validation fails.
            When False, return the error list.
        """
        errors: list[str] = []

        for table_name, table_schema in cls.tables.items():
            records = getattr(dataset, table_name, None)

            if records is None:
                errors.append(f"{table_name}: missing dataset table")
                continue

            if not isinstance(records, list):
                errors.append(f"{table_name}: expected list, got {type(records).__name__}")
                continue

            errors.extend(table_schema.validate_records(records))

        if errors and raise_on_error:
            raise SchemaValidationError(errors)

        return errors

    @classmethod
    def validate_record(
        cls,
        table_name: str,
        record: Mapping[str, Any],
        *,
        raise_on_error: bool = True,
    ) -> list[str]:
        """Validate one record for a known table."""
        if table_name not in cls.tables:
            raise KeyError(f"Unknown dataset table: {table_name}")

        errors = cls.tables[table_name].validate_records([record])

        if errors and raise_on_error:
            raise SchemaValidationError(errors)

        return errors

    @classmethod
    def to_dict(cls) -> dict[str, Any]:
        """Return the schema as a JSON-serializable dictionary."""
        return {
            "schema_version": cls.version,
            "tables": {
                table_name: table_schema.to_dict()
                for table_name, table_schema in cls.tables.items()
            },
        }

    @classmethod
    def to_json(cls) -> str:
        """Return the schema as pretty-printed JSON."""
        return json.dumps(cls.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def write(cls, path: str | Path) -> Path:
        """Write the schema to JSON.

        If ``path`` is a directory or has no ``.json`` suffix, the schema is
        written to ``path / "dataset_schema_v1.json"``.
        """
        output_path = Path(path)

        if output_path.suffix != ".json":
            output_path.mkdir(parents=True, exist_ok=True)
            output_path = output_path / "dataset_schema_v1.json"
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(cls.to_json(), encoding="utf-8")
        return output_path
