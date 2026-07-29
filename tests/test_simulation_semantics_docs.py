from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SEMANTICS_DOC = DOCS / "simulation-semantics-v1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_simulation_semantics_document_declares_its_status() -> None:
    text = _read(SEMANTICS_DOC)

    expected_content = [
        "# Simulation Semantics V1",
        "**Current behavior**",
        "**Target contract**",
        "**Unsupported behavior**",
        "## 16. Public-alpha semantic blockers",
    ]

    for item in expected_content:
        assert item in text


def test_simulation_semantics_documents_model_loop_order() -> None:
    text = _read(SEMANTICS_DOC)

    event_index = text.index("Process events due at the current model time")
    step_index = text.index("Call model.step()")
    counter_index = text.index("Increment model.steps by 1")
    recording_index = text.index("Collect registered model and agent observations")

    assert event_index < step_index < counter_index < recording_index


def test_simulation_semantics_documents_known_limitations() -> None:
    text = _read(SEMANTICS_DOC)

    expected_statements = [
        "an agent removed during the pass may still receive its callback",
        "does not automatically isolate current and next state",
        "does not automatically collect an initial time-zero observation",
        "does not provide transactional rollback",
        "does not provide component-independent random streams",
        "must not be treated as a continuous-time",
    ]

    for statement in expected_statements:
        assert statement in text


def test_simulation_semantics_documents_target_contracts() -> None:
    text = _read(SEMANTICS_DOC)

    expected_statements = [
        "Agents added during the pass are deferred until a future pass.",
        "An agent removed before its turn does not receive a later callback",
        "fractional absolute event times will be rejected",
        "require an explicit two-phase capability",
        "versioned named streams",
        "Execution status and scientific analysis eligibility",
    ]

    for statement in expected_statements:
        assert statement in text


def test_related_pages_link_to_normative_semantics() -> None:
    related_pages = [
        "scheduling.md",
        "delayed-events.md",
        "recording.md",
        "agent-lifecycle.md",
        "model-lifecycle.md",
    ]
    expected_link = "[Simulation Semantics V1](simulation-semantics-v1.md)"

    for filename in related_pages:
        assert expected_link in _read(DOCS / filename), filename


def test_mkdocs_navigation_includes_semantics_document() -> None:
    text = _read(ROOT / "mkdocs.yml")
    expected_entry = "- Simulation Semantics V1: simulation-semantics-v1.md"

    assert expected_entry in text
    assert text.count(expected_entry) == 1
