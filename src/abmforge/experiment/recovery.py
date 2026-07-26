"""Utilities for recovering partially completed experiments."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from abmforge.experiment.run_index import (
    RUN_IDENTITY_SCHEMA_VERSION,
    RunIndex,
    RunIndexEntry,
)
from abmforge.experiment.scenario import Scenario


@dataclass(frozen=True, slots=True)
class RunKey:
    """Deterministic identity for one planned experiment run."""

    model_name: str
    model_module: str
    model_qualname: str
    run_identity_version: str
    scenario: str
    seed: int | None
    steps: int | None
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
        # Programmatic stop conditions are arbitrary Python callables and do not
        # yet have a persisted, stable execution identity. Treat such scenarios
        # as missing rather than risk matching a scientifically different run.
        if scenario.stop_when is not None:
            missing.append(scenario)
            continue

        key = _canonical_run_key(
            model_name=scenario.model.__name__,
            model_module=scenario.model.__module__,
            model_qualname=scenario.model.__qualname__,
            run_identity_version=RUN_IDENTITY_SCHEMA_VERSION,
            scenario=scenario.name,
            seed=scenario.seed,
            steps=scenario.steps,
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
    model_module: str,
    model_qualname: str,
    run_identity_version: str,
    scenario: str | None,
    seed: int | None,
    steps: int | None,
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
        model_module=model_module,
        model_qualname=model_qualname,
        run_identity_version=run_identity_version,
        scenario=scenario or model_name,
        seed=seed,
        steps=steps,
        parameters=canonical_parameters,
    )


def _key_from_entry(entry: RunIndexEntry) -> RunKey:
    model_name = entry.model_name or ""

    return _canonical_run_key(
        model_name=model_name,
        model_module=entry.model_module or "",
        model_qualname=entry.model_qualname or "",
        run_identity_version=entry.run_identity_version or "",
        scenario=entry.scenario,
        seed=entry.seed,
        steps=entry.steps,
        parameters=entry.parameters,
    )
