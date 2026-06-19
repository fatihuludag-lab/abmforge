from pathlib import Path


def test_scheduling_docs_include_builtin_schedulers() -> None:
    text = Path("docs/scheduling.md").read_text(encoding="utf-8")

    assert "SequentialActivation" in text
    assert "RandomActivation" in text
    assert "SimultaneousActivation" in text
    assert "StagedActivation" in text


def test_scheduling_docs_describe_reproducibility_and_lifecycle_rules() -> None:
    text = Path("docs/scheduling.md").read_text(encoding="utf-8")

    assert "model-level random number generator" in text
    assert "same model state and seed" in text
    assert "Dead agents" in text
    assert "Newly spawned agents" in text
    assert "is_alive == False" in text


def test_scheduling_docs_include_scheduler_choice_guidance() -> None:
    text = Path("docs/scheduling.md").read_text(encoding="utf-8")

    assert "Choosing a scheduler" in text
    assert "Activation order affects results" in text
    assert "synchronous update" in text
