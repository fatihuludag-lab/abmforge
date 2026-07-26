from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PluginContext:
    """State passed to plugin lifecycle hooks."""

    experiment: Any | None = None
    archive: Any | None = None
    scenario: Any | None = None
    result: Any | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
