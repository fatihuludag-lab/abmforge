from pathlib import Path


def test_scheduling_docs_include_builtin_schedulers() -> None:
    text = Path("docs/scheduling.md").read_text(encoding="utf-8")

    assert "SequentialActivation" in text
    assert "RandomActivation" in text
    assert "SimultaneousActivation" in text
    assert "StagedActivation" in text


def test_scheduling_docs_describe_reproducibility_and_lifecycle_rules() -> None:
    text = Path("docs/scheduling.md").read_text(encoding="utf-8")

    assert "named `scheduler` random stream" in text
    assert "same candidate history, model seed, and scheduler-stream draw history" in text
    assert "Dead agents" in text
    assert "Newly spawned agents" in text
    assert "is_alive == False" in text


def test_scheduling_docs_include_scheduler_choice_guidance() -> None:
    text = Path("docs/scheduling.md").read_text(encoding="utf-8")

    assert "Choosing a scheduler" in text
    assert "Activation order affects results" in text
    assert "synchronous update" in text


def test_scheduling_docs_describe_strict_simultaneous_contract() -> None:
    text = Path("docs/scheduling.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    expected = [
        "Before any callback runs",
        "callable `step()` and `advance()` methods",
        "identifies every invalid agent",
        "No activation callback is executed",
        "no-op `advance()` method",
        "preflight validation finishes before any callback is invoked",
    ]

    for statement in expected:
        assert statement in normalized

    assert "living agents that define it" not in normalized


def test_scheduling_docs_describe_named_scheduler_stream() -> None:
    text = Path("docs/scheduling.md").read_text(
        encoding="utf-8",
    )
    normalized = " ".join(text.split())

    expected = [
        "named `scheduler` random stream",
        '`model.rng_stream("scheduler")`',
        "default `model.rng` stream remains available",
        "unrelated behavior draws do not change later activation order",
        "`AgentCollection.shuffle_do()`",
        "shuffled `StagedActivation`",
    ]

    for statement in expected:
        assert statement in normalized

    assert "using the model-level random number generator" not in normalized
