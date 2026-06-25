from __future__ import annotations

from abmforge import Scenario


def test_policy_template_baseline_runs() -> None:
    scenario = Scenario.from_yaml("configs/baseline.yaml")
    result = scenario.run()

    assert result.status == "completed"
    assert result.steps == 50
    assert len(result.dataset.model_records) > 0
    assert len(result.dataset.agent_records) > 0
