from __future__ import annotations

from typing import Final, Literal, TypeAlias

AgentLifecycleStatus: TypeAlias = Literal[
    "active",
    "removed",
]

ACTIVE: Final[AgentLifecycleStatus] = "active"
REMOVED: Final[AgentLifecycleStatus] = "removed"

VALID_AGENT_LIFECYCLE_STATUSES: Final[frozenset[str]] = frozenset(
    {
        ACTIVE,
        REMOVED,
    }
)


def validate_agent_lifecycle_status(status: str) -> AgentLifecycleStatus:
    """Validate and return an agent lifecycle status."""
    if status not in VALID_AGENT_LIFECYCLE_STATUSES:
        allowed = ", ".join(sorted(VALID_AGENT_LIFECYCLE_STATUSES))
        raise ValueError(f"Invalid agent lifecycle status: {status!r}. Expected one of: {allowed}")

    return status  # type: ignore[return-value]
