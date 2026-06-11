from __future__ import annotations

import importlib.util
from pathlib import Path

from abmforge import Experiment

SCHELLING_PATH = Path(__file__).resolve().parents[1] / "schelling" / "run.py"
SPEC = importlib.util.spec_from_file_location("schelling_example", SCHELLING_PATH)

if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Could not load Schelling example from {SCHELLING_PATH}")

schelling_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(schelling_module)

SchellingModel = schelling_module.SchellingModel


if __name__ == "__main__":
    experiment = Experiment(
        model=SchellingModel,
        parameters={
            "width": [20],
            "height": [20],
            "density": [0.6, 0.8],
            "homophily": [0.3, 0.5, 0.7],
        },
        seeds=[1, 2, 3],
        steps=50,
        name="schelling-parameter-sweep",
    )

    result = experiment.run()

    print("Parameter sweep completed.")
    print(result.summary())

    output_dir = result.write_csv("outputs/parameter_sweep")
    print(f"CSV output written to {output_dir}")
