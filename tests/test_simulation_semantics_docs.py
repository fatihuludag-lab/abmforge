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


def test_simulation_semantics_documents_removal_aware_activation() -> None:
    text = _read(SEMANTICS_DOC)
    normalized = " ".join(text.split())

    expected_statements = [
        "shared callback-time activation eligibility rule",
        "the collection still stores the same object under that identifier",
        "an agent added during the pass is deferred until a future pass",
        "an agent removed before its turn is skipped",
        "neither the removed snapshot object nor the newly added replacement",
        "self-removal is safe",
    ]

    for statement in expected_statements:
        assert statement in normalized

    assert "an agent removed during the pass may still receive its callback" not in normalized
    assert "### 5.3 Target collection contract" not in text


def test_simulation_semantics_documents_known_limitations() -> None:
    text = _read(SEMANTICS_DOC)

    expected_statements = [
        "does not automatically isolate current and next state",
        "does not automatically collect an initial time-zero observation",
        "does not provide transactional rollback",
        "does not provide component-independent random streams",
        "must not be treated as a continuous-time",
    ]

    for statement in expected_statements:
        assert statement in text


def test_simulation_semantics_documents_remaining_target_contracts() -> None:
    text = _read(SEMANTICS_DOC)

    expected_statements = [
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


def test_simulation_semantics_lists_remaining_public_alpha_blockers() -> None:
    text = _read(SEMANTICS_DOC)
    normalized = " ".join(text.split())

    remaining_blockers = [
        "Fractional event times are accepted without exact fractional-time execution.",
        "Valid stopped runs may be excluded from default analysis reports.",
        "Simultaneous activation does not require a complete two-phase agent contract.",
        "Scheduler randomness and agent behavior share one RNG stream.",
        "Agent-collection-space lifecycle invariants are not uniformly enforced.",
        "Canonical models lack sufficient scientific invariant and metamorphic tests.",
    ]

    for blocker in remaining_blockers:
        assert blocker in normalized

    assert "Collection bulk operations may invoke agents removed earlier" not in normalized
    assert "Removal-aware callback eligibility for collection bulk operations" in normalized


def test_related_pages_document_activation_eligibility() -> None:
    scheduling = _read(DOCS / "scheduling.md")
    lifecycle = _read(DOCS / "agent-lifecycle.md")

    assert "## Activation Eligibility" in scheduling
    assert "callback-time activation eligibility validation" in scheduling
    assert "agents removed before their turn are skipped" in scheduling

    assert "## Activation-Pass Removal Semantics" in lifecycle
    assert "An agent removed before its turn is skipped" in lifecycle
    assert "identity equality with the object currently stored" in lifecycle
