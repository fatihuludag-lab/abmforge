from __future__ import annotations

import json
from pathlib import Path

import pytest

from abmforge.experiment.archive import ExperimentArchive
from abmforge.experiment.config import ExperimentConfig, write_experiment_outputs


def _write_demo_model(tmp_path: Path) -> None:
    (tmp_path / "study_model.py").write_text(
        """
from abmforge import Agent, Model
from abmforge.scheduling import RandomActivation


class DemoAgent(Agent):
    def step(self):
        self.value += self.model.increment


class DemoModel(Model):
    def setup(self):
        self.n = int(self.parameters.get("n", 5))
        self.increment = int(self.parameters.get("increment", 1))
        self.agents.create(DemoAgent, n=self.n, value=0)
        self.scheduler = RandomActivation(self)
        self.record.metric("total_value", lambda model: model.agents.sum("value"))

    def step(self):
        self.scheduler.step()
""",
        encoding="utf-8",
    )


def test_experiment_config_loads_seed_count(tmp_path, monkeypatch) -> None:
    _write_demo_model(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    path = tmp_path / "experiment.yaml"
    path.write_text(
        """
name: demo-experiment
model: study_model.DemoModel

base_parameters:
  n: 5

experiment:
  parameters:
    increment: [1, 2]
  seeds:
    count: 3
    master_seed: 123

run:
  steps: 4

outputs:
  primary_metric: total_value
""",
        encoding="utf-8",
    )

    config = ExperimentConfig.from_yaml(path)

    assert config.name == "demo-experiment"
    assert config.model_path == "study_model.DemoModel"
    assert config.base_parameters == {"n": 5}
    assert config.parameters == {"increment": [1, 2]}
    assert len(config.seeds) == 3
    assert config.steps == 4
    assert config.primary_metric == "total_value"
    assert config.experiment_parameters() == {"n": [5], "increment": [1, 2]}


def test_experiment_config_supports_explicit_seed_list(tmp_path, monkeypatch) -> None:
    _write_demo_model(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    path = tmp_path / "experiment.yaml"
    path.write_text(
        """
model: study_model.DemoModel

experiment:
  parameters:
    increment: [1]
  seeds: [10, 11]

run:
  steps: 2
""",
        encoding="utf-8",
    )

    config = ExperimentConfig.from_yaml(path)

    assert config.seeds == [10, 11]


def test_experiment_config_rejects_parameter_overlap(tmp_path, monkeypatch) -> None:
    _write_demo_model(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    path = tmp_path / "experiment.yaml"
    path.write_text(
        """
model: study_model.DemoModel

base_parameters:
  increment: 1

experiment:
  parameters:
    increment: [1, 2]
  seeds: [1]

run:
  steps: 2
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="both 'base_parameters'"):
        ExperimentConfig.from_yaml(path)


def test_experiment_config_runs_and_writes_outputs(tmp_path, monkeypatch) -> None:
    _write_demo_model(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    path = tmp_path / "experiment.yaml"
    path.write_text(
        """
name: demo-experiment
model: study_model.DemoModel
base_parameters:
  n: 4
experiment:
  parameters:
    increment: [1, 2]
  seeds: [100, 101]
run:
  steps: 3
outputs:
  primary_metric: total_value
""",
        encoding="utf-8",
    )

    config = ExperimentConfig.from_yaml(path)
    result = config.to_experiment().run()
    output = write_experiment_outputs(
        result,
        config,
        path,
        tmp_path / "outputs",
    )

    assert (output / "configs" / "experiment.yaml").exists()
    assert (output / "data").exists()
    assert (output / "data" / "runs.json").exists()
    assert (output / "data" / "runs.csv").exists()
    assert (output / "manifest.json").exists()
    assert (output / "dataset_schema.json").exists()
    assert (output / "run_index.json").exists()
    assert (output / "reports" / "experiment_summary.json").exists()
    assert (output / "reports" / "README_RESULTS.md").exists()

    archive = ExperimentArchive(output)
    assert archive.validate() == []
    assert len(archive.read_run_index().entries) == 4

    summary = json.loads(
        (output / "reports" / "experiment_summary.json").read_text(encoding="utf-8")
    )
    assert summary["run_count_expected"] == 4
    assert summary["primary_metric"] == "total_value"
    assert summary["archive_format"] == "experiment-archive-v1"
    assert summary["csv_compatibility_outputs"] is True
