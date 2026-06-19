from __future__ import annotations

import heapq
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from abmforge.time.event import Event
from abmforge.time.status import CANCELLED, EXECUTED, FAILED, SCHEDULED

if TYPE_CHECKING:
    from abmforge.core.model import Model


class EventQueue:
    """Deterministic event queue with owner and tag-based cancellation."""

    def __init__(self, model: Model) -> None:
        self.model = model
        self._heap: list[tuple[float, int, int, int]] = []
        self._events: dict[int, Event] = {}
        self._next_id = 1
        self._sequence = 0

    def schedule(
        self,
        *,
        callback: Callable[[], Any],
        at: float | None = None,
        after: float | None = None,
        priority: int = 0,
        owner: int | str | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        cancel_on_owner_removed: bool = True,
    ) -> Event:
        """Schedule a callback.

        Exactly one of ``at`` or ``after`` must be provided.
        """
        if (at is None) == (after is None):
            raise ValueError("provide exactly one of at or after")

        if at is not None:
            event_time = float(at)
        else:
            assert after is not None
            event_time = self.model.time + float(after)
        if event_time < self.model.time:
            raise ValueError("cannot schedule an event in the past")

        event_id = self._next_id
        self._next_id += 1
        self._sequence += 1

        event = Event(
            event_id=event_id,
            time=event_time,
            priority=priority,
            sequence=self._sequence,
            callback=callback,
            owner=owner,
            tags=tuple(tags or ()),
            cancel_on_owner_removed=cancel_on_owner_removed,
        )
        self._events[event_id] = event
        heapq.heappush(self._heap, (event.time, event.priority, event.sequence, event.event_id))
        self.model.record.event(
            event_id=event_id,
            owner=owner,
            tags=list(event.tags),
            status=SCHEDULED,
        )
        return event

    def cancel(self, event_id: int) -> bool:
        """Cancel an event by id. Returns True when an event was cancelled."""
        event = self._events.get(event_id)
        if event is None or event.cancelled:
            return False
        event.cancelled = True
        self.model.record.event(
            event_id=event.event_id,
            owner=event.owner,
            tags=list(event.tags),
            status=CANCELLED,
        )
        return True

    def cancel_by_owner(self, owner: int | str) -> int:
        """Cancel all future events owned by ``owner``."""
        count = 0
        for event in list(self._events.values()):
            if (
                event.owner == owner
                and event.cancel_on_owner_removed
                and self.cancel(event.event_id)
            ):
                count += 1
        return count

    def cancel_by_tag(self, tag: str) -> int:
        """Cancel all future events containing ``tag``."""
        count = 0
        for event in list(self._events.values()):
            if tag in event.tags and self.cancel(event.event_id):
                count += 1
        return count

    def events_for_owner(self, owner: int | str) -> list[Event]:
        """Return non-cancelled events owned by ``owner``."""
        return [
            event for event in self._events.values() if event.owner == owner and not event.cancelled
        ]

    def process_due(self, *, time: float) -> int:
        """Execute all due events. Returns the number of executed events."""
        executed = 0
        while self._heap and self._heap[0][0] <= time:
            _, _, _, event_id = heapq.heappop(self._heap)
            event = self._events.get(event_id)
            if event is None:
                continue
            if event.cancelled:
                continue

            try:
                event.callback()
            except Exception:
                self.model.record.event(
                    event_id=event.event_id,
                    owner=event.owner,
                    tags=list(event.tags),
                    status=FAILED,
                )
                raise
            else:
                executed += 1
                self.model.record.event(
                    event_id=event.event_id,
                    owner=event.owner,
                    tags=list(event.tags),
                    status=EXECUTED,
                )
            finally:
                self._events.pop(event_id, None)
        return executed

    def pending_count(self) -> int:
        """Return the number of non-cancelled future events."""
        return sum(1 for event in self._events.values() if not event.cancelled)
