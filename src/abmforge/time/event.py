from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Event:
    """Scheduled callback in model time."""

    event_id: int
    time: float
    priority: int
    sequence: int
    callback: Callable[[], Any]
    owner: int | str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)
    cancel_on_owner_removed: bool = True
    cancelled: bool = False
