from __future__ import annotations

from pathlib import Path

from abmforge.time.queue import EventQueue

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _normalized(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return " ".join(text.split())


def test_event_queue_methods_document_integer_ticks() -> None:
    assert EventQueue.schedule_at.__doc__ is not None
    assert EventQueue.schedule_after.__doc__ is not None

    assert "absolute fixed-step integer tick" in EventQueue.schedule_at.__doc__
    assert "non-negative integer-tick delay" in EventQueue.schedule_after.__doc__


def test_delayed_events_documents_accepted_tick_values() -> None:
    text = _normalized(DOCS / "delayed-events.md")

    expected = [
        "Fixed-Step Integer-Tick Contract",
        "non-negative integer-valued simulation ticks",
        "Integer-valued floats such as `1.0` are accepted",
        "schedule_at(3.0",
        "schedule_after(2.0",
    ]

    for statement in expected:
        assert statement in text


def test_delayed_events_documents_rejected_values() -> None:
    text = _normalized(DOCS / "delayed-events.md")

    expected = [
        "fractional absolute event times",
        "fractional delays",
        "Boolean values",
        "implicit numeric coercion",
        "non-finite values",
        "negative delays",
        "absolute times earlier than the current model time",
    ]

    for statement in expected:
        assert statement in text


def test_rejected_scheduling_is_documented_as_side_effect_free() -> None:
    text = _normalized(DOCS / "delayed-events.md")

    expected = [
        "consume an event identifier",
        "create a pending event",
        "write an event record",
    ]

    for statement in expected:
        assert statement in text


def test_delayed_events_rejects_continuous_time_claim() -> None:
    text = _normalized(DOCS / "delayed-events.md")

    assert "not a continuous-time or general discrete-event simulation engine" in text


def test_simulation_semantics_documents_integer_tick_execution() -> None:
    text = _normalized(DOCS / "simulation-semantics-v1.md")

    expected = [
        "accepts only finite, integer-valued event ticks",
        "fractional absolute event times",
        "fractional delays",
        "implicit numeric coercion",
        "consume an event identifier",
        "create a pending event",
        "write an event record",
        "before `model.step()` when `model.time == t`",
        "not a continuous-time or general discrete-event simulation engine",
    ]

    for statement in expected:
        assert statement in text


def test_fractional_time_is_removed_from_public_alpha_blockers() -> None:
    text = _normalized(DOCS / "simulation-semantics-v1.md")

    assert "Fractional event times are accepted without exact fractional-time execution" not in text
    assert (
        "strict integer-tick event scheduling are now part of the current runtime guarantee" in text
    )


def test_api_reference_documents_fixed_step_integer_ticks() -> None:
    text = _normalized(DOCS / "api.md")

    expected = [
        "accepts only finite, integer-valued event ticks",
        "rejects fractional or past ticks",
        "rejects fractional or negative delays",
        "Boolean values, strings, and objects accepted only through implicit",
        "Integer-valued floats such as `1.0` are accepted",
        "hybrid or continuous-time execution",
    ]

    for statement in expected:
        assert statement in text
