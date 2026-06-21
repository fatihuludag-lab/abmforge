from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from abmforge.data.dataset import Dataset
from abmforge.data.storage.parquet import ParquetStorage
from abmforge.experiment.registry import ExperimentRegistry

ArchiveFormat = Literal["json", "parquet"]

_DATASET_JSON_FILES = {
    "runs": "runs.json",
    "model_records": "model_records.jsonl",
    "agent_records": "agent_records.jsonl",
    "event_records": "event_records.jsonl",
    "lifecycle_records": "lifecycle_records.jsonl",
    "errors": "errors.jsonl",
}

_DATASET_PARQUET_FILES = {
    "runs": "runs.parquet",
    "model_records": "model_records.parquet",
    "agent_records": "agent_records.parquet",
    "event_records": "event_records.parquet",
    "lifecycle_records": "lifecycle_records.parquet",
    "errors": "errors.parquet",
}


def _canonical_json_bytes(data: Any) -> bytes:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")


def _sha256_json(data: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(data)).hexdigest()


def _read_json_array(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, list):
        raise ValueError(f"{path.name} must contain a JSON array")

    records: list[dict[str, Any]] = []

    for index, record in enumerate(data):
        if not isinstance(record, dict):
            raise ValueError(f"{path.name}[{index}] must be a JSON object")
        records.append(record)

    return records


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    if not path.read_text(encoding="utf-8").strip():
        return records

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()

            if not line:
                continue

            record = json.loads(line)

            if not isinstance(record, dict):
                raise ValueError(f"{path.name}:{line_number} must be a JSON object")

            records.append(record)

    return records


@dataclass(slots=True)
class ExperimentArchive:
    """Directory-based archive for ABMForge experiment outputs."""

    path: Path

    @classmethod
    def create(cls, path: str | Path, *, overwrite: bool = False) -> ExperimentArchive:
        archive_path = Path(path)

        if archive_path.exists():
            if not overwrite:
                raise FileExistsError(
                    f"Archive path already exists: {archive_path}. "
                    "Pass overwrite=True to replace it."
                )

            if archive_path.is_dir():
                shutil.rmtree(archive_path)
            else:
                archive_path.unlink()

        archive_path.mkdir(parents=True, exist_ok=False)
        for subdir in ("data", "snapshots", "reports", "logs", "configs"):
            (archive_path / subdir).mkdir(exist_ok=False)
        return cls(path=archive_path)

    @property
    def data_dir(self) -> Path:
        return self.path / "data"

    @property
    def snapshots_dir(self) -> Path:
        return self.path / "snapshots"

    @property
    def reports_dir(self) -> Path:
        return self.path / "reports"

    @property
    def logs_dir(self) -> Path:
        return self.path / "logs"

    @property
    def configs_dir(self) -> Path:
        return self.path / "configs"

    @property
    def manifest_path(self) -> Path:
        return self.path / "manifest.json"

    @property
    def dataset_schema_path(self) -> Path:
        return self.path / "dataset_schema.json"

    @property
    def registry_path(self) -> Path:
        return self.path / "registry.json"

    def create_registry(self, *, experiment_id: str | None = None) -> ExperimentRegistry:
        """Create a new registry for this experiment archive."""
        registry = ExperimentRegistry(experiment_id=experiment_id or f"experiment-{uuid4().hex}")
        registry.write(self.registry_path)
        return registry

    def read_registry(self) -> ExperimentRegistry:
        """Read the archive registry."""
        return ExperimentRegistry.read(self.registry_path)

    def ensure_registry(self) -> ExperimentRegistry:
        """Read the archive registry, creating it if necessary."""
        if self.registry_path.exists():
            return self.read_registry()

        return self.create_registry()

    def write_scenario_file(
        self,
        source: str | Path,
        *,
        filename: str = "scenario.yaml",
    ) -> Path:
        """Copy the Scenario YAML file into the archive configs directory."""
        source_path = Path(source)

        if not source_path.is_file():
            raise FileNotFoundError(f"Scenario file does not exist: {source_path}")

        self.configs_dir.mkdir(exist_ok=True)
        destination = self.configs_dir / filename
        shutil.copy2(source_path, destination)

        return destination

    def write_dataset_json(self, dataset: Dataset) -> Path:
        """Write dataset tables into the archive data directory as JSON/JSONL."""
        return dataset.write_json(self.data_dir)

    def write_dataset_parquet(self, dataset: Dataset) -> Path:
        """Write dataset tables into the archive data directory as Parquet files."""
        storage = ParquetStorage(run_id=dataset.run_id)
        storage.runs = list(dataset.runs)
        storage.model_records = list(dataset.model_records)
        storage.agent_records = list(dataset.agent_records)
        storage.event_records = list(dataset.event_records)
        storage.lifecycle_records = list(dataset.lifecycle_records)
        storage.errors = list(dataset.errors)
        return storage.write_parquet(self.data_dir)

    def write_dataset_schema(self, dataset: Dataset) -> Path:
        """Write the dataset schema into the archive root."""
        return dataset.write_schema(self.dataset_schema_path)

    def write_manifest(self, dataset: Dataset) -> Path:
        """Write a reproducibility manifest into the archive root."""
        return dataset.write_manifest(self.manifest_path)

    def write_run_outputs(
        self,
        dataset: Dataset,
        *,
        format: ArchiveFormat = "json",
    ) -> None:
        """Write minimum reproducible run outputs."""
        dataset.validate()

        if format == "json":
            self.write_dataset_json(dataset)
        elif format == "parquet":
            self.write_dataset_parquet(dataset)
        else:
            raise ValueError(f"Unsupported archive format: {format}")

        self.write_dataset_schema(dataset)
        self.write_manifest(dataset)

    def validate(self) -> list[str]:
        """Return archive validation errors.

        An empty list means the archive satisfies the current minimum contract.
        """
        errors: list[str] = []

        if not self.path.exists():
            return [f"Archive does not exist: {self.path}"]

        for subdir in ("data", "snapshots", "reports", "logs", "configs"):
            if not (self.path / subdir).is_dir():
                errors.append(f"Missing directory: {subdir}")

        if not self.manifest_path.is_file():
            errors.append("Missing manifest.json")

        if not self.dataset_schema_path.is_file():
            errors.append("Missing dataset_schema.json")

        if self.data_dir.exists() and not any(self.data_dir.iterdir()):
            errors.append("Data directory is empty")

        if errors:
            return errors

        errors.extend(self._validate_dataset_schema_hash())
        errors.extend(self._validate_json_dataset_integrity())
        errors.extend(self._validate_parquet_dataset_integrity())

        return errors

    def _validate_dataset_schema_hash(self) -> list[str]:
        """Validate manifest dataset schema hash against dataset_schema.json."""
        try:
            manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            schema = json.loads(self.dataset_schema_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return [f"Invalid JSON while validating archive metadata: {exc}"]

        expected_hash = manifest.get("dataset_schema_hash")

        if expected_hash is None:
            return ["manifest.json is missing dataset_schema_hash"]

        actual_hash = _sha256_json(schema)

        if actual_hash != expected_hash:
            return [
                "dataset_schema_hash mismatch: "
                f"manifest has {expected_hash}, actual is {actual_hash}"
            ]

        return []

    def _validate_json_dataset_integrity(self) -> list[str]:
        """Validate JSON/JSONL dataset files against manifest counts and hashes.

        Parquet archive integrity validation is intentionally deferred to a later PR.
        This method only runs when JSON archive files are present.
        """
        runs_path = self.data_dir / _DATASET_JSON_FILES["runs"]

        if not runs_path.exists():
            return []

        errors: list[str] = []

        try:
            manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return [f"Invalid manifest.json: {exc}"]

        record_counts = manifest.get("record_counts", {})
        record_hashes = manifest.get("record_hashes", {})

        if not isinstance(record_counts, dict):
            errors.append("manifest.json record_counts must be an object")
            record_counts = {}

        if not isinstance(record_hashes, dict):
            errors.append("manifest.json record_hashes must be an object")
            record_hashes = {}

        for table_name, filename in _DATASET_JSON_FILES.items():
            table_path = self.data_dir / filename

            if not table_path.exists():
                errors.append(f"Missing dataset table file: data/{filename}")
                continue

            try:
                if filename.endswith(".jsonl"):
                    records = _read_jsonl(table_path)
                else:
                    records = _read_json_array(table_path)
            except (json.JSONDecodeError, ValueError) as exc:
                errors.append(f"Invalid dataset table data/{filename}: {exc}")
                continue

            expected_count = record_counts.get(table_name)
            actual_count = len(records)

            if expected_count is None:
                errors.append(f"manifest.json record_counts missing table: {table_name}")
            elif actual_count != expected_count:
                errors.append(
                    f"record_counts mismatch for {table_name}: "
                    f"manifest has {expected_count}, actual is {actual_count}"
                )

            expected_hash = record_hashes.get(table_name)
            actual_hash = _sha256_json(records)

            if expected_hash is None:
                errors.append(f"manifest.json record_hashes missing table: {table_name}")
            elif actual_hash != expected_hash:
                errors.append(
                    f"record_hashes mismatch for {table_name}: "
                    f"manifest has {expected_hash}, actual is {actual_hash}"
                )

        return errors

    def _validate_parquet_dataset_integrity(self) -> list[str]:
        """Validate Parquet dataset files against manifest record counts.

        JSON/JSONL archives are validated separately through
        ``_validate_json_dataset_integrity``. This method only runs when at
        least one expected Parquet table file is present.
        """
        if not any(
            (self.data_dir / filename).exists() for filename in _DATASET_PARQUET_FILES.values()
        ):
            return []

        errors: list[str] = []

        try:
            import pandas as pd
        except ModuleNotFoundError:
            return [
                "Parquet archive validation requires pandas and pyarrow. "
                "Install with: pip install abmforge[data]"
            ]

        try:
            manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return [f"Invalid manifest.json: {exc}"]

        record_counts = manifest.get("record_counts", {})
        if not isinstance(record_counts, dict):
            errors.append("manifest.json record_counts must be an object")
            record_counts = {}

        for table_name, filename in _DATASET_PARQUET_FILES.items():
            table_path = self.data_dir / filename

            if not table_path.exists():
                errors.append(f"Missing dataset table file: data/{filename}")
                continue

            try:
                frame = pd.read_parquet(table_path)
            except Exception as exc:
                errors.append(f"Invalid parquet dataset table data/{filename}: {exc}")
                continue

            expected_count = record_counts.get(table_name)
            actual_count = len(frame)

            if expected_count is None:
                errors.append(f"manifest.json record_counts missing table: {table_name}")
            elif actual_count != expected_count:
                errors.append(
                    f"record_counts mismatch for {table_name}: "
                    f"manifest has {expected_count}, actual is {actual_count}"
                )

        return errors
