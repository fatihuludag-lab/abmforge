from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from abmforge.core.model import Model
    from abmforge.data.dataset import Dataset


@dataclass(slots=True)
class RunResult:
    """Result of a single scenario run."""

    run_id: str
    model: Model
    dataset: Dataset
    status: str
    steps: int
    stop_reason: str | None
