from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from abmforge.core.model import Model


class Scheduler(ABC):
    """Base class for agent activation strategies."""

    def __init__(self, model: Model) -> None:
        self.model = model

    def to_metadata(self) -> dict[str, object]:
        """Return JSON-serializable scheduler audit metadata.

        This is metadata for inspection and snapshots. It is not a scheduler
        restore contract.
        """

        return {
            "schema_version": "scheduler-metadata-v1",
            "scheduler_type": type(self).__name__,
            "module": type(self).__module__,
            "attached": True,
        }

    @abstractmethod
    def step(self) -> None:
        """Activate agents for one model step."""
