from __future__ import annotations

from abmforge import Scenario


def main() -> None:
    scenario = Scenario.from_yaml("configs/baseline.yaml")
    result = scenario.run()

    print(f"Run ID: {result.run_id}")
    print(f"Status: {result.status}")
    print(f"Steps: {result.steps}")
    print(f"Model records: {len(result.dataset.model_records)}")
    print(f"Agent records: {len(result.dataset.agent_records)}")

    result.dataset.write_csv("outputs/baseline_csv")
    print("CSV output written to outputs/baseline_csv")


if __name__ == "__main__":
    main()
