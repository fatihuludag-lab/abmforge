from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from abmforge import ODDDocument, ReproducibilityManifest, Scenario

try:
    from model_zoo.sir.model import SIRModel
except ModuleNotFoundError:
    from model import SIRModel


def build_odd_document() -> ODDDocument:
    """Build ODD skeleton for the SIR model zoo example."""
    odd = ODDDocument.from_model(
        SIRModel,
        purpose=(
            "Demonstrate how local spatial contact between agents can produce "
            "epidemic diffusion over time."
        ),
        authors=["Fatih Uludağ"],
        entities=["Person", "Grid cell"],
        scales={
            "time": "discrete simulation step",
            "space": "two-dimensional toroidal grid",
            "epidemiological_state": "susceptible, infected, recovered",
        },
        process_overview=[
            "Each infected person contacts neighbouring agents within Chebyshev radius 1.",
            "Susceptible neighbours may become infected with probability infection_prob.",
            "Infected agents may recover with probability recovery_prob.",
            "The model records susceptible, infected, recovered, and attack_rate metrics.",
        ],
        design_concepts={
            "stochasticity": (
                "Transmission, recovery, placement, and random "
                "activation are controlled by the model RNG."
            ),
            "emergence": (
                "Population-level epidemic curves emerge from local contact and transition events."
            ),
            "interaction": "Agents interact through spatial neighbourhood contact.",
        },
        initialization=[
            "Create a toroidal grid.",
            "Place agents randomly on the grid.",
            "Initialize a configurable number of agents as infected.",
            "Initialize all remaining agents as susceptible.",
        ],
        submodels=[
            {
                "name": "transmission",
                "description": "An infected person may infect susceptible neighbours.",
                "source": "Person.step",
            },
            {
                "name": "recovery",
                "description": "An infected person may transition to recovered.",
                "source": "Person.step",
            },
        ],
    )
    odd.add_state_variable(
        "Person",
        "state",
        description="Disease state: susceptible, infected, or recovered.",
        kind="categorical",
    )
    odd.add_state_variable(
        "Grid cell",
        "occupants",
        description="Zero or more persons occupying the grid cell.",
        kind="list",
    )
    return odd


def _last_metric(records: list[dict[str, Any]], metric: str) -> Any:
    for record in reversed(records):
        if record.get("metric") == metric:
            return record.get("value")
    raise KeyError(f"Metric not found: {metric}")


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser for the SIR model zoo example."""
    parser = argparse.ArgumentParser(prog="python model_zoo/sir/run.py")
    parser.add_argument("--width", type=int, default=30)
    parser.add_argument("--height", type=int, default=30)
    parser.add_argument("--n-agents", type=int, default=300)
    parser.add_argument("--initial-infected", type=int, default=5)
    parser.add_argument("--infection-prob", type=float, default=0.25)
    parser.add_argument("--recovery-prob", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/model_zoo/sir"),
    )
    parser.add_argument(
        "--include-packages",
        action="store_true",
        help="Include installed package metadata in manifest output.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the SIR model zoo example."""
    args = build_parser().parse_args(argv)

    scenario = Scenario(
        model=SIRModel,
        seed=args.seed,
        steps=args.steps,
        name="model-zoo-sir",
        parameters={
            "width": args.width,
            "height": args.height,
            "n_agents": args.n_agents,
            "initial_infected": args.initial_infected,
            "infection_prob": args.infection_prob,
            "recovery_prob": args.recovery_prob,
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
            "model_zoo_example": "sir",
            "archive_role": "teaching-and-research-example",
        },
    ).write(output_dir)

    odd = build_odd_document()
    odd.write_markdown(output_dir)
    odd.write_json(output_dir)

    print("model_zoo=sir")
    print(f"status={result.status}")
    print(f"run_id={result.run_id}")
    print(f"output_dir={output_dir}")
    print(f"final_susceptible={_last_metric(result.dataset.model_records, 'susceptible')}")
    print(f"final_infected={_last_metric(result.dataset.model_records, 'infected')}")
    print(f"final_recovered={_last_metric(result.dataset.model_records, 'recovered')}")
    print(f"final_attack_rate={_last_metric(result.dataset.model_records, 'attack_rate')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
