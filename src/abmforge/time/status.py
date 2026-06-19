from __future__ import annotations

from typing import Final, Literal, TypeAlias

EventStatus: TypeAlias = Literal[
    "scheduled",
    "cancelled",
    "executed",
    "failed",
]

SCHEDULED: Final[EventStatus] = "scheduled"
CANCELLED: Final[EventStatus] = "cancelled"
EXECUTED: Final[EventStatus] = "executed"
FAILED: Final[EventStatus] = "failed"

VALID_EVENT_STATUSES: Final[frozenset[str]] = frozenset(
    {
        SCHEDULED,
        CANCELLED,
        EXECUTED,
        FAILED,
    }
)


def validate_event_status(status: str) -> EventStatus:
    """Validate and return an event lifecycle status."""
    if status not in VALID_EVENT_STATUSES:
        allowed = ", ".join(sorted(VALID_EVENT_STATUSES))
        raise ValueError(f"Invalid event status: {status!r}. Expected one of: {allowed}")

    return status  # type: ignore[return-value]
