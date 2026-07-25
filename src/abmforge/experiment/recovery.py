"""Utilities for recovering partially completed experiments."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from abmforge.experiment.run_index import RunIndex, RunIndexEntry
from abmforge.experiment.scenario import Scenario


@dataclass(frozen=True, slots=True)
class RunKey:
    """Deterministic identity for one planned experiment run."""

    model_name: str
    scenario: str
    seed: int | None
    parameters: str


def completed_run_keys(run_index: RunIndex) -> Counter[RunKey]:
    """Return completed archived runs as a multiset of deterministic keys."""
    keys: Counter[RunKey] = Counter()

    for entry in run_index.entries:
        if entry.status != "completed":
            continue

        keys[_key_from_entry(entry)] += 1

    return keys


def missing_scenarios(
    scenarios: Iterable[Scenario],
    run_index: RunIndex,
) -> list[Scenario]:
    """Return planned scenarios not already completed in an archive."""
    completed = completed_run_keys(run_index)
    missing: list[Scenario] = []

    for scenario in scenarios:
        key = _canonical_run_key(
            model_name=scenario.model.__name__,
            scenario=scenario.name,
            seed=scenario.seed,
            parameters=scenario.parameters,
        )

        if completed[key] > 0:
            completed[key] -= 1
            continue

        missing.append(scenario)

    return missing


def _canonical_run_key(
    *,
    model_name: str,
    scenario: str | None,
    seed: int | None,
    parameters: dict[str, Any],
) -> RunKey:
    canonical_parameters = json.dumps(
        parameters,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )

    return RunKey(
        model_name=model_name,
        scenario=scenario or model_name,
        seed=seed,
        parameters=canonical_parameters,
    )


def _key_from_entry(entry: RunIndexEntry) -> RunKey:
    model_name = entry.model_name or ""

    return _canonical_run_key(
        model_name=model_name,
        scenario=entry.scenario,
        seed=entry.seed,
        parameters=entry.parameters,
    )
