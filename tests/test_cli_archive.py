from __future__ import annotations

import pytest

from abmforge.cli.main import main
from abmforge.data.dataset import Dataset
from abmforge.experiment.archive import ExperimentArchive


def test_cli_validate_archive_passes(tmp_path, capsys):
    dataset = Dataset(run_id="run-1")
    dataset.add_run(
        run_id="run-1",
        scenario="test_scenario",
        model_name="TestModel",
        parameters={},
        seed=1,
        status="completed",
    )

    archive = ExperimentArchive.create(tmp_path / "archive")
    archive.write_run_outputs(dataset)

    main(["validate", str(archive.path)])

    captured = capsys.readouterr()
    assert "Archive validation passed" in captured.out


def test_cli_validate_archive_fails(tmp_path, capsys):
    archive = ExperimentArchive.create(tmp_path / "archive")

    with pytest.raises(SystemExit) as exc_info:
        main(["validate", str(archive.path)])

    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "Archive validation failed" in captured.out
