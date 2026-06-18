from pathlib import Path

from abmforge.experiment.scenario import Scenario


def test_wealth_baseline_scenario_yaml_runs() -> None:
    scenario_path = Path("examples/scenarios/wealth_baseline.yaml")

    scenario = Scenario.from_yaml(scenario_path)
    result = scenario.run()

    assert result.status == "completed"
    assert result.steps == 10
    assert result.dataset.runs
    assert result.dataset.model_records
