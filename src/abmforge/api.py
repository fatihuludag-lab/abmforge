"""Declared public API surface for ABMForge.

This module is intentionally import-light. It records the top-level import
contract used by ``abmforge.__init__`` and by public API regression tests.
When a public import is added, removed, or reclassified, update this file and
the API stability documentation in the same pull request.
"""

from __future__ import annotations

PUBLIC_API: tuple[str, ...] = (
    "Agent",
    "AgentCollection",
    "AdvanceableAgent",
    "AgentID",
    "AgentLike",
    "StatefulAgent",
    "SteppableAgent",
    "ContinuousSpace",
    "Recorder",
    "Dataset",
    "DATASET_SCHEMA_VERSION",
    "DatasetSchemaV1",
    "Event",
    "EventQueue",
    "Experiment",
    "ExperimentArchive",
    "ExperimentRegistry",
    "ExperimentResult",
    "GISSpace",
    "GridWorld",
    "Model",
    "NetworkSpace",
    "ODDDocument",
    "ParameterGrid",
    "RandomActivation",
    "ReplayValidationReport",
    "ReproducibilityManifest",
    "RunResult",
    "SALibProblem",
    "Scenario",
    "Scheduler",
    "SchemaValidationError",
    "SensitivityAnalysis",
    "SequentialActivation",
    "SimultaneousActivation",
    "StagedActivation",
    "__version__",
    "analyze_morris",
    "analyze_sobol",
    "attach_snapshot_hash",
    "link_snapshot",
    "plot_grid",
    "plot_multiple_runs",
    "plot_timeseries",
    "read_snapshot",
    "sample_morris",
    "sample_sobol",
    "snapshot_hash",
    "validate_replay",
    "write_snapshot",
)

STABLE_ALPHA_API: tuple[str, ...] = (
    "__version__",
    "Agent",
    "AgentCollection",
    "Model",
    "Scenario",
    "Experiment",
    "ExperimentResult",
    "RunResult",
    "ParameterGrid",
    "Dataset",
    "Recorder",
)

PROVISIONAL_API: tuple[str, ...] = (
    "DATASET_SCHEMA_VERSION",
    "DatasetSchemaV1",
    "SchemaValidationError",
    "ExperimentArchive",
    "ExperimentRegistry",
    "ReproducibilityManifest",
    "ODDDocument",
    "AdvanceableAgent",
    "AgentID",
    "AgentLike",
    "StatefulAgent",
    "SteppableAgent",
    "Scheduler",
    "SequentialActivation",
    "RandomActivation",
    "SimultaneousActivation",
    "StagedActivation",
    "GridWorld",
    "NetworkSpace",
    "ContinuousSpace",
    "GISSpace",
    "Event",
    "EventQueue",
)

EXPERIMENTAL_API: tuple[str, ...] = (
    "ReplayValidationReport",
    "read_snapshot",
    "write_snapshot",
    "snapshot_hash",
    "attach_snapshot_hash",
    "link_snapshot",
    "validate_replay",
    "SALibProblem",
    "SensitivityAnalysis",
    "sample_sobol",
    "sample_morris",
    "analyze_sobol",
    "analyze_morris",
    "plot_timeseries",
    "plot_multiple_runs",
    "plot_grid",
)

API_STABILITY_LEVELS: dict[str, tuple[str, ...]] = {
    "stable_alpha": STABLE_ALPHA_API,
    "provisional": PROVISIONAL_API,
    "experimental": EXPERIMENTAL_API,
}


def _ensure_unique(names: tuple[str, ...], *, label: str) -> None:
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        duplicate_list = ", ".join(duplicates)
        msg = f"{label} contains duplicate public API names: {duplicate_list}"
        raise RuntimeError(msg)


def _ensure_partition() -> None:
    _ensure_unique(PUBLIC_API, label="PUBLIC_API")

    declared_names: tuple[str, ...] = (
        *STABLE_ALPHA_API,
        *PROVISIONAL_API,
        *EXPERIMENTAL_API,
    )
    _ensure_unique(declared_names, label="API stability declarations")

    public_names = set(PUBLIC_API)
    stability_names = set(declared_names)

    missing = sorted(public_names - stability_names)
    extra = sorted(stability_names - public_names)

    if missing or extra:
        msg = (
            "API stability declarations must partition PUBLIC_API. "
            f"Missing declarations: {missing}. Extra declarations: {extra}."
        )
        raise RuntimeError(msg)


_ensure_partition()
