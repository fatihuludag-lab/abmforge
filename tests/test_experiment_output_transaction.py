from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from abmforge.core.model import Model
from abmforge.experiment.config import (
    ExperimentConfig,
    write_experiment_outputs,
)


def _config() -> ExperimentConfig:
    return ExperimentConfig(
        name="transaction-test",
        model=Model,
        model_path="tests.TransactionModel",
        base_parameters={},
        parameters={"population": [10]},
        seeds=[42],
        steps=1,
        primary_metric=None,
    )


def _result() -> Mock:
    result = Mock()

    result.run_records.return_value = []
    result.model_records.return_value = []
    result.agent_records.return_value = []
    result.event_records.return_value = []
    result.lifecycle_records.return_value = []
    result.error_records.return_value = []
    result.summary.return_value = {}

    return result


def test_experiment_output_failure_preserves_existing_archive(
    tmp_path: Path,
) -> None:
    target = tmp_path / "archive"
    target.mkdir()
    old_marker = target / "old.txt"
    old_marker.write_text("old archive", encoding="utf-8")

    config_path = tmp_path / "experiment.yaml"
    config_path.write_text("name: test\n", encoding="utf-8")

    result = _result()
    result.write_csv.side_effect = RuntimeError("simulated CSV failure")

    with pytest.raises(RuntimeError, match="simulated CSV failure"):
        write_experiment_outputs(
            result,
            _config(),
            config_path,
            target,
            overwrite=True,
        )

    assert old_marker.read_text(encoding="utf-8") == "old archive"

    transaction_artifacts = [
        path for path in tmp_path.iterdir() if ".staging-" in path.name or ".backup-" in path.name
    ]
    assert transaction_artifacts == []


def test_experiment_output_success_replaces_existing_archive(
    tmp_path: Path,
) -> None:
    target = tmp_path / "archive"
    target.mkdir()
    old_marker = target / "old.txt"
    old_marker.write_text("old archive", encoding="utf-8")

    config_path = tmp_path / "experiment.yaml"
    config_path.write_text("name: test\n", encoding="utf-8")

    result = _result()

    output_path = write_experiment_outputs(
        result,
        _config(),
        config_path,
        target,
        overwrite=True,
    )

    assert output_path == target
    assert target.is_dir()
    assert not old_marker.exists()
    assert (target / "configs" / "experiment.yaml").is_file()
    assert (target / "reports" / "experiment_summary.json").is_file()
    assert (target / "reports" / "README_RESULTS.md").is_file()

    transaction_artifacts = [
        path for path in tmp_path.iterdir() if ".staging-" in path.name or ".backup-" in path.name
    ]
    assert transaction_artifacts == []
