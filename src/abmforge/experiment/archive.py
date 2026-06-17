from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from abmforge.data.dataset import Dataset


@dataclass(slots=True)
class ExperimentArchive:
    """Directory-based archive for ABMForge experiment outputs."""

    path: Path

    @classmethod
    def create(cls, path: str | Path, *, overwrite: bool = False) -> ExperimentArchive:
        archive_path = Path(path)

        if archive_path.exists() and overwrite:
            shutil.rmtree(archive_path)

        archive_path.mkdir(parents=True, exist_ok=True)

        for subdir in ("data", "snapshots", "reports", "logs"):
            (archive_path / subdir).mkdir(exist_ok=True)

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
    def manifest_path(self) -> Path:
        return self.path / "manifest.json"

    @property
    def dataset_schema_path(self) -> Path:
        return self.path / "dataset_schema.json"

    def write_dataset_json(self, dataset: Dataset) -> Path:
        """Write dataset tables into the archive data directory as JSON/JSONL."""
        return dataset.write_json(self.data_dir)

    def write_dataset_schema(self, dataset: Dataset) -> Path:
        """Write the dataset schema into the archive root."""
        return dataset.write_schema(self.dataset_schema_path)

    def write_manifest(self, dataset: Dataset) -> Path:
        """Write a reproducibility manifest into the archive root."""
        return dataset.write_manifest(self.manifest_path)

    def write_run_outputs(self, dataset: Dataset) -> None:
        """Write minimum reproducible run outputs."""
        dataset.validate()
        self.write_dataset_json(dataset)
        self.write_dataset_schema(dataset)
        self.write_manifest(dataset)

    def validate(self) -> list[str]:
        """Return archive validation errors.

        An empty list means the archive satisfies the current minimum contract.
        """
        errors: list[str] = []

        if not self.path.exists():
            return [f"Archive does not exist: {self.path}"]

        for subdir in ("data", "snapshots", "reports", "logs"):
            if not (self.path / subdir).is_dir():
                errors.append(f"Missing directory: {subdir}")

        if not self.manifest_path.is_file():
            errors.append("Missing manifest.json")

        if not self.dataset_schema_path.is_file():
            errors.append("Missing dataset_schema.json")

        if not any(self.data_dir.iterdir()) if self.data_dir.exists() else True:
            errors.append("Data directory is empty")

        return errors
