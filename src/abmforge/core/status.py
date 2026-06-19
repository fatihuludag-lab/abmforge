from __future__ import annotations

from typing import Final, Literal, TypeAlias

ModelStatus: TypeAlias = Literal[
    "created",
    "running",
    "completed",
    "stopped",
    "failed",
]

CREATED: Final[ModelStatus] = "created"
RUNNING: Final[ModelStatus] = "running"
COMPLETED: Final[ModelStatus] = "completed"
STOPPED: Final[ModelStatus] = "stopped"
FAILED: Final[ModelStatus] = "failed"

VALID_MODEL_STATUSES: Final[frozenset[str]] = frozenset(
    {
        CREATED,
        RUNNING,
        COMPLETED,
        STOPPED,
        FAILED,
    }
)


def validate_model_status(status: str) -> ModelStatus:
    """Validate and return a model lifecycle status."""
    if status not in VALID_MODEL_STATUSES:
        allowed = ", ".join(sorted(VALID_MODEL_STATUSES))
        raise ValueError(f"Invalid model status: {status!r}. Expected one of: {allowed}")

    return status  # type: ignore[return-value]
