from __future__ import annotations

from model import WealthModel

from abmforge import Scenario

scenario = Scenario(model=WealthModel, parameters={"n": 100}, seed=42, steps=10)
result = scenario.run()

print(f"run_id={result.run_id}")
print(f"status={result.status}")
print(result.dataset.model_records[-2:])
