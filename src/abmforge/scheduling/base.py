from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from abmforge.core.model import Model


class Scheduler(ABC):
    """Base class for agent activation strategies."""

    def __init__(self, model: Model) -> None:
        self.model = model

    @abstractmethod
    def step(self) -> None:
        """Activate agents for one model step."""
