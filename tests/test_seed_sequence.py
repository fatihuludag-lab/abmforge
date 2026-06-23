from pathlib import Path

import pytest

from abmforge.experiment import DEFAULT_MAX_SEED, SeedSequence


def test_seed_sequence_generate_is_deterministic() -> None:
    first = SeedSequence(base_seed=123).generate(10)
    second = SeedSequence(base_seed=123).generate(10)

    assert first == second


def test_seed_sequence_generate_changes_with_base_seed() -> None:
    first = SeedSequence(base_seed=123).generate(10)
    second = SeedSequence(base_seed=124).generate(10)

    assert first != second


def test_seed_sequence_generate_returns_unique_seeds_in_range() -> None:
    seeds = SeedSequence(base_seed=123).generate(100)

    assert len(seeds) == 100
    assert len(set(seeds)) == 100
    assert all(0 <= seed <= DEFAULT_MAX_SEED for seed in seeds)


def test_seed_sequence_start_changes_generated_sequence() -> None:
    sequence = SeedSequence(base_seed=123)

    first = sequence.generate(5, start=0)
    second = sequence.generate(5, start=5)

    assert first != second
    assert len(set(first + second)) == 10


def test_seed_sequence_label_changes_generated_sequence() -> None:
    sequence = SeedSequence(base_seed=123)

    baseline = sequence.generate(5, label="baseline")
    policy = sequence.generate(5, label="policy")

    assert baseline != policy


def test_seed_sequence_derive_is_deterministic() -> None:
    sequence = SeedSequence(base_seed=123)

    first = sequence.derive(parameter_index=2, replicate_index=3)
    second = sequence.derive(parameter_index=2, replicate_index=3)

    assert first == second


def test_seed_sequence_derive_changes_by_parameter_and_replicate() -> None:
    sequence = SeedSequence(base_seed=123)

    seeds = {
        sequence.derive(parameter_index=0, replicate_index=0),
        sequence.derive(parameter_index=0, replicate_index=1),
        sequence.derive(parameter_index=1, replicate_index=0),
        sequence.derive(parameter_index=1, replicate_index=1),
    }

    assert len(seeds) == 4


def test_seed_sequence_supports_custom_seed_range() -> None:
    seeds = SeedSequence(base_seed=123, max_seed=99).generate(20)

    assert len(seeds) == 20
    assert len(set(seeds)) == 20
    assert all(0 <= seed <= 99 for seed in seeds)


@pytest.mark.parametrize(
    ("kwargs", "error_type"),
    [
        ({"base_seed": -1}, ValueError),
        ({"base_seed": True}, TypeError),
        ({"base_seed": 1, "max_seed": 0}, ValueError),
        ({"base_seed": 1, "namespace": ""}, ValueError),
    ],
)
def test_seed_sequence_validates_constructor_arguments(
    kwargs: dict[str, object],
    error_type: type[Exception],
) -> None:
    with pytest.raises(error_type):
        SeedSequence(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("method", "kwargs", "error_type"),
    [
        ("generate", {"count": -1}, ValueError),
        ("generate", {"count": True}, TypeError),
        ("generate", {"count": 2, "start": -1}, ValueError),
        ("generate", {"count": 2, "label": 7}, TypeError),
        ("derive", {"parameter_index": -1}, ValueError),
        ("derive", {"replicate_index": True}, TypeError),
        ("derive", {"run_index": -1}, ValueError),
        ("derive", {"label": 7}, TypeError),
    ],
)
def test_seed_sequence_validates_method_arguments(
    method: str,
    kwargs: dict[str, object],
    error_type: type[Exception],
) -> None:
    sequence = SeedSequence(base_seed=123)

    with pytest.raises(error_type):
        getattr(sequence, method)(**kwargs)


def test_seed_sequence_policy_doc_is_in_mkdocs_nav() -> None:
    docs = Path("docs/seed-sequence-policy.md").read_text(encoding="utf-8")
    mkdocs = Path("mkdocs.yml").read_text(encoding="utf-8")

    assert "Seed Sequence Policy" in docs
    assert "Seed Sequence Policy: seed-sequence-policy.md" in mkdocs
