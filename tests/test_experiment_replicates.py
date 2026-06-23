from __future__ import annotations

import pytest

from abmforge.experiment import (
    ReplicatePlanEntry,
    SeedSequence,
    build_replicate_plan,
)


def _records(plan: list[ReplicatePlanEntry]) -> list[dict[str, int]]:
    return [entry.to_dict() for entry in plan]


def test_build_replicate_plan_creates_parameter_major_entries() -> None:
    plan = build_replicate_plan(
        parameter_count=2,
        replicates=3,
        seed_sequence=SeedSequence(base_seed=123),
    )

    assert [(entry.parameter_index, entry.replicate_index, entry.run_index) for entry in plan] == [
        (0, 0, 0),
        (0, 1, 1),
        (0, 2, 2),
        (1, 0, 3),
        (1, 1, 4),
        (1, 2, 5),
    ]
    assert len({entry.seed for entry in plan}) == 6
    assert all(isinstance(entry.seed, int) for entry in plan)


def test_build_replicate_plan_is_deterministic() -> None:
    first = build_replicate_plan(
        parameter_count=3,
        replicates=2,
        seed_sequence=SeedSequence(base_seed=123),
    )
    second = build_replicate_plan(
        parameter_count=3,
        replicates=2,
        seed_sequence=SeedSequence(base_seed=123),
    )

    assert _records(first) == _records(second)


def test_build_replicate_plan_changes_when_base_seed_changes() -> None:
    first = build_replicate_plan(
        parameter_count=2,
        replicates=2,
        seed_sequence=SeedSequence(base_seed=123),
    )
    second = build_replicate_plan(
        parameter_count=2,
        replicates=2,
        seed_sequence=SeedSequence(base_seed=124),
    )

    assert [entry.seed for entry in first] != [entry.seed for entry in second]


def test_build_replicate_plan_respects_label() -> None:
    first = build_replicate_plan(
        parameter_count=2,
        replicates=2,
        seed_sequence=SeedSequence(base_seed=123),
        label="baseline",
    )
    second = build_replicate_plan(
        parameter_count=2,
        replicates=2,
        seed_sequence=SeedSequence(base_seed=123),
        label="policy",
    )

    assert [entry.seed for entry in first] != [entry.seed for entry in second]


def test_build_replicate_plan_respects_start_run_index() -> None:
    sequence = SeedSequence(base_seed=123)

    plan = build_replicate_plan(
        parameter_count=1,
        replicates=2,
        seed_sequence=sequence,
        start_run_index=10,
    )

    assert [entry.run_index for entry in plan] == [10, 11]
    assert [entry.seed for entry in plan] == sequence.generate(2, start=10)


def test_build_replicate_plan_supports_zero_dimensions() -> None:
    sequence = SeedSequence(base_seed=123)

    assert (
        build_replicate_plan(
            parameter_count=0,
            replicates=3,
            seed_sequence=sequence,
        )
        == []
    )
    assert (
        build_replicate_plan(
            parameter_count=3,
            replicates=0,
            seed_sequence=sequence,
        )
        == []
    )


def test_build_replicate_plan_rejects_invalid_counts() -> None:
    sequence = SeedSequence(base_seed=123)

    with pytest.raises(ValueError, match="parameter_count must be >= 0"):
        build_replicate_plan(
            parameter_count=-1,
            replicates=1,
            seed_sequence=sequence,
        )

    with pytest.raises(ValueError, match="replicates must be >= 0"):
        build_replicate_plan(
            parameter_count=1,
            replicates=-1,
            seed_sequence=sequence,
        )

    with pytest.raises(TypeError, match="start_run_index must be an integer"):
        build_replicate_plan(
            parameter_count=1,
            replicates=1,
            seed_sequence=sequence,
            start_run_index=True,  # type: ignore[arg-type]
        )


def test_build_replicate_plan_rejects_non_seed_sequence() -> None:
    with pytest.raises(TypeError, match="seed_sequence must be a SeedSequence"):
        build_replicate_plan(
            parameter_count=1,
            replicates=1,
            seed_sequence=object(),  # type: ignore[arg-type]
        )


def test_build_replicate_plan_rejects_more_runs_than_seed_space() -> None:
    with pytest.raises(ValueError, match="count cannot exceed"):
        build_replicate_plan(
            parameter_count=2,
            replicates=2,
            seed_sequence=SeedSequence(base_seed=123, max_seed=2),
        )


def test_replicate_plan_entry_to_dict() -> None:
    entry = ReplicatePlanEntry(
        parameter_index=1,
        replicate_index=2,
        run_index=5,
        seed=123456,
    )

    assert entry.to_dict() == {
        "parameter_index": 1,
        "replicate_index": 2,
        "run_index": 5,
        "seed": 123456,
    }
