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
        "**Stability:** Public-alpha semantic baseline",
        "## 16. Public-alpha semantic status",
        "No unresolved public-alpha semantic blockers remain",
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
    normalized = " ".join(text.split())

    expected_statements = [
        "does not automatically isolate current and next state",
        "does not automatically collect an initial time-zero observation",
        "does not provide transactional rollback",
        "is not a continuous-time or general discrete-event simulation engine",
    ]

    for statement in expected_statements:
        assert statement in normalized


def test_simulation_semantics_documents_remaining_target_contracts() -> None:
    text = _read(SEMANTICS_DOC)

    expected_statements = [
        "distinguish event creation, requested execution, and actual execution",
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


def test_simulation_semantics_reports_public_alpha_completion() -> None:
    text = _read(SEMANTICS_DOC)
    normalized = " ".join(text.split())

    expected = [
        "## 16. Public-alpha semantic status",
        "No unresolved public-alpha semantic blockers remain",
        (
            "Canonical Model Zoo models now include explicit scientific "
            "invariant, boundary-case, metamorphic, and same-seed "
            "trajectory tests"
        ),
        "does not constitute empirical validation or calibration",
        "public-alpha semantic baseline",
        "scientific reference-model verification",
    ]

    for statement in expected:
        assert statement in normalized

    obsolete = [
        "Canonical models lack sufficient scientific invariant and metamorphic tests.",
        (
            "before the fixed-step execution profile can be treated as "
            "complete public-alpha semantics"
        ),
        "The remaining item concerns scientific interpretation",
    ]

    for statement in obsolete:
        assert statement not in normalized


def test_related_pages_document_activation_eligibility() -> None:
    scheduling = _read(DOCS / "scheduling.md")
    lifecycle = _read(DOCS / "agent-lifecycle.md")

    assert "## Activation Eligibility" in scheduling
    assert "callback-time activation eligibility validation" in scheduling
    assert "agents removed before their turn are skipped" in scheduling

    assert "## Activation-Pass Removal Semantics" in lifecycle
    assert "An agent removed before its turn is skipped" in lifecycle
    assert "identity equality with the object currently stored" in lifecycle


def test_simulation_semantics_documents_stopped_run_eligibility() -> None:
    text = _read(SEMANTICS_DOC)
    normalized = " ".join(text.split())

    expected = [
        "Execution status and scientific analysis eligibility are separate concepts",
        "`completed` and `stopped` runs as analysis-eligible",
        "at least one numeric final model metric is available",
        "`analysis_eligibility.csv`",
        "separation of execution status from analysis eligibility",
        "The resolved public-alpha semantic baseline includes",
    ]

    for statement in expected:
        assert statement in normalized

    assert "Valid stopped runs may be excluded from default analysis reports" not in normalized


def test_simulation_semantics_documents_strict_two_phase_activation() -> None:
    text = _read(SEMANTICS_DOC)
    normalized = " ".join(text.split())

    expected = [
        "validates every initially eligible candidate before the first callback",
        "callable `step()` and `advance()` methods",
        "reports all invalid candidates in one `TypeError`",
        "before any activation callback has run",
        "all remaining eligible `step()` callbacks",
        "all remaining eligible `advance()` callbacks",
        "explicit callable no-op `advance()` method",
        ("Strict two-phase simultaneous activation is part of the current runtime guarantee"),
    ]

    for statement in expected:
        assert statement in normalized

    obsolete = [
        "calls `advance()` only when the candidate remains eligible and defines that method",
        "does not currently require every participating agent to implement `advance()`",
        "an error when `advance()` is missing",
        "Simultaneous activation does not require a complete two-phase agent contract",
    ]

    for statement in obsolete:
        assert statement not in normalized


def test_simulation_semantics_documents_named_rng_streams() -> None:
    text = _read(SEMANTICS_DOC)
    normalized = " ".join(text.split())

    expected = [
        "`Model.rng` remains the default behavior stream",
        "`Model.rng_stream(name)` returns a cached named stream",
        "named `scheduler` stream",
        "Stream creation order does not affect another stream",
        "opened named stream states",
        "Legacy snapshots containing only `rng_state` remain restorable",
        "named scheduler random streams",
    ]

    for statement in expected:
        assert statement in normalized

    obsolete = [
        "generates a permutation using `model.rng`",
        "uses the same model-level random-number generator",
        "a fixed seed does not provide component-independent random streams",
        "A future random-stream contract will assign scheduler activation",
        "Scheduler randomness and agent behavior share one RNG stream",
    ]

    for statement in obsolete:
        assert statement not in normalized


def test_simulation_semantics_documents_managed_lifecycle_integrity() -> None:
    text = _read(SEMANTICS_DOC)
    normalized = " ".join(text.split())

    expected = [
        (
            "`AgentCollection.remove(...)` and `Model.remove_agent(...)` "
            "use the same managed lifecycle operation"
        ),
        "accepts only active living agents",
        "same identifier but a different object",
        "Spatial cleanup completes before lifecycle mutation",
        "Repeated removal raises `KeyError`",
        "Built-in spaces clear both `agent.pos` and `agent.world`",
        "`space.remove(...)` is spatial unplacement only",
        "uniform collection-space lifecycle integrity",
    ]

    for statement in expected:
        assert statement in normalized

    obsolete = [
        "Direct `AgentCollection.remove(...)` changes collection membership.",
        "Direct collection removal changes collection membership.",
        "Complete lifecycle cleanup from direct collection removal",
        "Agent-collection-space lifecycle invariants are not uniformly enforced.",
        "direct collection removal changes collection membership only",
    ]

    for statement in obsolete:
        assert statement not in normalized


def test_simulation_semantics_randomness_section_matches_named_stream_runtime() -> None:
    text = _read(SEMANTICS_DOC)
    normalized = " ".join(text.split())

    expected = [
        "### 14.1 Current generators",
        "`Model.rng` remains the default behavior stream",
        "`Model.rng_stream(name)` provides cached named component streams",
        "named `scheduler` stream",
        "`named-rng-streams-v1`",
    ]

    for statement in expected:
        assert statement in normalized

    obsolete = [
        "Each model creates one NumPy random-number generator from the model seed.",
        "The model, schedulers, and user behavior may consume this shared generator.",
        "The target design will use versioned named streams",
        "independent scheduler and agent streams;",
    ]

    for statement in obsolete:
        assert statement not in normalized
