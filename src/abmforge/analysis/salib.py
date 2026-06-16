from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class SALibProblem:
    """Problem definition for SALib-based sensitivity analysis."""

    bounds: dict[str, tuple[float, float]]

    @property
    def names(self) -> list[str]:
        return list(self.bounds.keys())

    def to_dict(self) -> dict[str, Any]:
        """Return the SALib-compatible problem dictionary."""
        return {
            "num_vars": len(self.bounds),
            "names": self.names,
            "bounds": [list(bound) for bound in self.bounds.values()],
        }


def _require_salib() -> None:
    try:
        import SALib  # noqa: F401
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "SALib integration requires SALib. Install it with: pip install SALib"
        ) from exc


def sample_sobol(
    problem: SALibProblem,
    *,
    n: int,
    calc_second_order: bool = True,
    seed: int | None = None,
) -> list[dict[str, float]]:
    """Generate Sobol samples as parameter dictionaries."""
    _require_salib()

    from SALib.sample import sobol

    samples = sobol.sample(
        problem.to_dict(),
        n,
        calc_second_order=calc_second_order,
        seed=seed,
    )

    return [dict(zip(problem.names, row, strict=True)) for row in samples]


def analyze_sobol(
    problem: SALibProblem,
    values: list[float],
    *,
    calc_second_order: bool = True,
) -> dict[str, Any]:
    """Analyze Sobol sensitivity indices for model outputs."""
    _require_salib()

    from SALib.analyze import sobol

    result = sobol.analyze(
        problem.to_dict(),
        values,
        calc_second_order=calc_second_order,
        print_to_console=False,
    )

    return {
        key: value.tolist() if hasattr(value, "tolist") else value for key, value in result.items()
    }


def sample_morris(
    problem: SALibProblem,
    *,
    n: int,
    num_levels: int = 4,
    seed: int | None = None,
) -> list[dict[str, float]]:
    """Generate Morris samples as parameter dictionaries."""
    _require_salib()

    from SALib.sample import morris

    samples = morris.sample(
        problem.to_dict(),
        n,
        num_levels=num_levels,
        seed=seed,
    )

    return [dict(zip(problem.names, row, strict=True)) for row in samples]


def analyze_morris(
    problem: SALibProblem,
    values: list[float],
    *,
    num_levels: int = 4,
) -> dict[str, Any]:
    """Analyze Morris sensitivity indices for model outputs."""
    _require_salib()

    from SALib.analyze import morris

    result = morris.analyze(
        problem.to_dict(),
        values,
        num_levels=num_levels,
        print_to_console=False,
    )

    return {
        key: value.tolist() if hasattr(value, "tolist") else value for key, value in result.items()
    }
