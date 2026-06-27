from __future__ import annotations

import abmforge
from abmforge.api import (
    API_STABILITY_LEVELS,
    EXPERIMENTAL_API,
    PROVISIONAL_API,
    PUBLIC_API,
    STABLE_ALPHA_API,
)


def test_public_api_exports_are_unique() -> None:
    assert len(abmforge.__all__) == len(set(abmforge.__all__))


def test_public_api_exports_match_declared_contract() -> None:
    assert tuple(abmforge.__all__) == PUBLIC_API


def test_public_api_exports_exist() -> None:
    for name in abmforge.__all__:
        assert hasattr(abmforge, name), name


def test_api_stability_groups_are_disjoint() -> None:
    groups = (STABLE_ALPHA_API, PROVISIONAL_API, EXPERIMENTAL_API)
    declared: list[str] = []

    for group in groups:
        declared.extend(group)

    assert len(declared) == len(set(declared))


def test_api_stability_groups_partition_public_api() -> None:
    declared = set(STABLE_ALPHA_API) | set(PROVISIONAL_API) | set(EXPERIMENTAL_API)

    assert declared == set(PUBLIC_API)


def test_api_stability_mapping_matches_group_constants() -> None:
    assert API_STABILITY_LEVELS == {
        "stable_alpha": STABLE_ALPHA_API,
        "provisional": PROVISIONAL_API,
        "experimental": EXPERIMENTAL_API,
    }


def test_stable_alpha_api_contains_core_research_entrypoints() -> None:
    expected = {
        "__version__",
        "Agent",
        "Model",
        "Scenario",
        "Experiment",
        "ParameterGrid",
        "Dataset",
        "Recorder",
    }

    assert expected <= set(STABLE_ALPHA_API)


def test_core_public_imports() -> None:
    from abmforge import Agent, Experiment, Model, ParameterGrid, Scenario

    assert Agent is not None
    assert Model is not None
    assert Scenario is not None
    assert Experiment is not None
    assert ParameterGrid is not None
