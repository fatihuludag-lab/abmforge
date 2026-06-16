from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from abmforge import ODDDocument, ReproducibilityManifest, Scenario

try:
    from model_zoo.schelling.model import SchellingModel
except ModuleNotFoundError:
    from model import SchellingModel


def build_odd_document() -> ODDDocument:
    """Build ODD skeleton for the Schelling model zoo example."""
    odd = ODDDocument.from_model(
        SchellingModel,
        purpose=(
            "Demonstrate how local homophily preferences among households can "
            "produce emergent spatial segregation."
        ),
        authors=["Fatih Uludağ"],
        entities=["Household", "Grid cell"],
        scales={
            "time": "discrete simulation step",
            "space": "two-dimensional toroidal grid",
            "social": "binary household group identity",
        },
        process_overview=[
            "Households observe neighbouring households within Chebyshev radius 1.",
            "A household is happy when the share of same-group neighbours is at least the homophily threshold.",
            "Unhappy households move to randomly selected empty cells.",
            "The model records population, empty cells, mean similarity, and unhappy households.",
        ],
        design_concepts={
            "emergence": (
                "Macro-level segregation emerges from local household relocation decisions."
            ),
            "stochasticity": (
                "Initial placement, group assignment, activation order, and relocation choices use the model RNG."
            ),
            "interaction": (
                "Households interact indirectly through local neighbourhood composition."
            ),
        },
        initialization=[
            "Create a toroidal grid with a configurable width and height.",
            "Place households on a random subset of grid cells according to the density parameter.",
            "Assign each household to one of two groups with equal probability.",
        ],
        submodels=[
            {
                "name": "household satisfaction",
                "description": "Calculate local same-group neighbour share.",
                "source": "Household.similarity",
            },
            {
                "name": "relocation",
                "description": "Move unhappy households to random empty cells.",
                "source": "SchellingModel.move_to_random_empty_cell",
            },
        ],
    )
    odd.add_state_variable(
        "Household",
        "group",
        description="Binary household group identity.",
        kind="integer",
    )
    odd.add_state_variable(
        "Household",
        "happy",
        description="Whether the household currently satisfies its local homophily preference.",
        kind="boolean",
    )
    odd.add_state_variable(
        "Grid cell",
        "occupancy",
        description="Whether a cell is empty or occupied by one household.",
        kind="categorical",
    )
    return odd


def _last_metric(records: list[dict[str, Any]], metric: str) -> Any:
    for record in reversed(records):
        if record.get("metric") == metric:
            return record.get("value")
    raise KeyError(f"Metric not found: {metric}")


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser for the Schelling model zoo example."""
    parser = argparse.ArgumentParser(prog="python model_zoo/schelling/run.py")
    parser.add_argument("--width", type=int, default=20)
    parser.add_argument("--height", type=int, default=20)
    parser.add_argument("--density", type=float, default=0.8)
    parser.add_argument("--homophily", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/model_zoo/schelling"),
    )
    parser.add_argument(
        "--include-packages",
        action="store_true",
        help="Include installed package metadata in manifest output.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Schelling model zoo example."""
    args = build_parser().parse_args(argv)

    scenario = Scenario(
        model=SchellingModel,
        seed=args.seed,
        steps=args.steps,
        name="model-zoo-schelling",
        parameters={
            "width": args.width,
            "height": args.height,
            "density": args.density,
            "homophily": args.homophily,
        },
    )

    result = scenario.run()
    result.dataset.validate()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    result.dataset.write_csv(output_dir)
    result.dataset.write_json(output_dir)
    result.dataset.write_schema(output_dir)

    ReproducibilityManifest.from_run_result(
        result,
        include_git=True,
        include_packages=args.include_packages,
        include_command=True,
        metadata={
            "model_zoo_example": "schelling",
            "archive_role": "teaching-and-research-example",
        },
    ).write(output_dir)

    odd = build_odd_document()
    odd.write_markdown(output_dir)
    odd.write_json(output_dir)

    print("model_zoo=schelling")
    print(f"status={result.status}")
    print(f"run_id={result.run_id}")
    print(f"output_dir={output_dir}")
    print(f"final_mean_similarity={_last_metric(result.dataset.model_records, 'mean_similarity')}")
    print(
        f"final_unhappy_households={_last_metric(result.dataset.model_records, 'unhappy_households')}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
