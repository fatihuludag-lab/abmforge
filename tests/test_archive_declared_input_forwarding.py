from pathlib import Path

import pytest

from abmforge import Model, Scenario
from abmforge.experiment.archive import ExperimentArchive


class InputModel(Model):
    def setup(self):
        self.record.metric("value", lambda m: int(Path(m.parameters["file"]).read_text()))


@pytest.mark.parametrize("method", ["write_manifest", "write_run_outputs"])
def test_declared_input_forwarded_and_archive_validates(tmp_path, method):
    source = tmp_path / "input.txt"
    source.write_text("3")
    dataset = (
        Scenario(
            InputModel,
            parameters={"file": str(source)},
            steps=1,
            seed=1,
            input_artifacts=[source],
            input_root=tmp_path,
        )
        .run()
        .dataset
    )
    archive = ExperimentArchive.create(tmp_path / "archive")
    if method == "write_manifest":
        archive.write_dataset_json(dataset)
        archive.write_dataset_schema(dataset)
        archive.write_run_index(dataset)
    getattr(archive, method)(dataset, input_artifacts=[source], input_root=tmp_path)
    assert archive.validate() == []
    # Validation uses preserved evidence, not the current original input bytes.
    source.write_text("4")
    assert archive.validate() == []


@pytest.mark.parametrize("mutation", ["changed", "omitted"])
def test_wrong_declarations_still_rejected(tmp_path, mutation):
    source = tmp_path / "input.txt"
    source.write_text("3")
    dataset = (
        Scenario(
            InputModel,
            parameters={"file": str(source)},
            steps=1,
            seed=1,
            input_artifacts=[source],
            input_root=tmp_path,
        )
        .run()
        .dataset
    )
    if mutation == "changed":
        source.write_text("4")
    inputs = [source] if mutation == "changed" else []
    archive = ExperimentArchive.create(tmp_path / "archive")
    with pytest.raises(ValueError, match="declared input identity"):
        archive.write_run_outputs(dataset, input_artifacts=inputs, input_root=tmp_path)
