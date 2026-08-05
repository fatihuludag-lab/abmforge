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
from abmforge.repro.execution_fingerprint import (
    ExecutionFingerprintV1,
    canonical_parameters_sha256,
)


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
    execution_fingerprint_digest: str = ""


def completed_run_keys(run_index: RunIndex) -> Counter[RunKey]:
    """Return safely reusable completed archived runs as deterministic keys."""
    keys: Counter[RunKey] = Counter()

    for entry in run_index.entries:
        if entry.status != "completed":
            continue

        fingerprint = _trusted_fingerprint_from_entry(entry)
        if fingerprint is None:
            continue

        keys[_key_from_entry(entry, fingerprint)] += 1

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

        fingerprint = scenario.execution_fingerprint()
        if not fingerprint.trusted:
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
            execution_fingerprint_digest=fingerprint.digest,
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
    execution_fingerprint_digest: str = "",
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
        execution_fingerprint_digest=execution_fingerprint_digest,
    )


def _key_from_entry(
    entry: RunIndexEntry,
    fingerprint: ExecutionFingerprintV1,
) -> RunKey:
    return _canonical_run_key(
        model_name=fingerprint.model_name,
        model_module=fingerprint.model_module,
        model_qualname=fingerprint.model_qualname,
        run_identity_version=entry.run_identity_version or "",
        scenario=fingerprint.scenario,
        seed=fingerprint.seed,
        steps=fingerprint.steps,
        parameters=entry.parameters,
        execution_fingerprint_digest=fingerprint.digest,
    )


def _trusted_fingerprint_from_entry(
    entry: RunIndexEntry,
) -> ExecutionFingerprintV1 | None:
    if entry.run_identity_version != RUN_IDENTITY_SCHEMA_VERSION:
        return None
    if entry.execution_fingerprint is None:
        return None

    fingerprint = ExecutionFingerprintV1.from_dict(entry.execution_fingerprint)
    if fingerprint is None or not fingerprint.trusted:
        return None

    scenario = entry.scenario or entry.model_name or ""
    if (
        entry.model_name != fingerprint.model_name
        or entry.model_module != fingerprint.model_module
        or entry.model_qualname != fingerprint.model_qualname
        or scenario != fingerprint.scenario
        or entry.seed != fingerprint.seed
        or entry.steps != fingerprint.steps
        or canonical_parameters_sha256(entry.parameters) != fingerprint.parameters_sha256
    ):
        return None

    return fingerprint
